import os
import sys
import logging
from datetime import datetime
from functools import wraps

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

from translator.model_loader import HFModelClient
from translator.prompt_builder import build_translation_prompt
from translator.prompt_generator import build_pattern_aware_prompt
from translator.response_parser import parse_llm_response
from translator.module3 import parse_code, get_code_summary, detect_pattern, map_pattern
from translator.doc_service import DocumentationService
from run_in_sandbox import execute_python

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(env_path)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

SUPPORTED_LANGUAGES = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", 
    "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala"
]

MAX_CODE_LENGTH = int(os.getenv("MAX_CODE_LENGTH", 10000))

try:
    model_client = HFModelClient()
    logger.info("Model client initialized successfully")
except ValueError as e:
    logger.warning(f"Configuration Error: {e}")
    model_client = None


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_key = os.getenv("API_KEY")
        if not expected_key:
            return f(*args, **kwargs)
        if api_key != expected_key:
            return jsonify({"success": False, "error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def log_request():
    logger.info(f"{request.method} {request.path} from {request.remote_addr}")


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "model": os.getenv("MODEL_ID"),
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/languages", methods=["GET"])
def get_supported_languages():
    return jsonify({"success": True, "languages": SUPPORTED_LANGUAGES, "count": len(SUPPORTED_LANGUAGES)})


@app.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json(force=True)
        if data is None:
            return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
        
        source_code = data.get("source_code")
        src_lang = data.get("src_lang") or data.get("source_language", "Java")
        tgt_lang = data.get("tgt_lang") or data.get("target_language", "Python")
        
        if not source_code:
            return jsonify({"success": False, "error": "Missing required field: source_code"}), 400
        
        code_length = len(source_code)
        if code_length > MAX_CODE_LENGTH:
            return jsonify({"success": False, "error": f"Code exceeds max length of {MAX_CODE_LENGTH}"}), 400
        
        # Check if model is available - use demo mode if not
        if model_client is None:
            logger.warning("Model client not available, returning demo response")
            
            # Generate demo translation based on simple patterns
            demo_translation = source_code
            
            demo_explanation = f"This is a {src_lang} code snippet that would be translated to {tgt_lang}. To enable real translation, please configure your HuggingFace API key in the .env file."
            
            demo_alternatives = source_code
            
            # Try pattern detection even without API
            pattern_result = None
            try:
                pattern = detect_pattern(source_code, src_lang)
                if pattern:
                    alternatives_p = map_pattern(pattern)
                    pattern_result = {
                        "pattern": pattern,
                        "confidence": 0.85,
                        "alternatives": alternatives_p.get("alternatives", "") if alternatives_p else "",
                        "code_example": alternatives_p.get("code_example", "") if alternatives_p else ""
                    }
            except Exception as e:
                logger.warning(f"Pattern detection error: {e}")
            
            # Always provide a default pattern if none detected
            if pattern_result is None:
                pattern_result = {
                    "pattern": "Sequential Execution",
                    "confidence": 0.75,
                    "alternatives": "Basic code that runs sequentially from top to bottom",
                    "code_example": "# No specific design pattern detected\n# This is simple sequential code"
                }
            
            return jsonify({
                "success": True,
                "translated_code": demo_translation,
                "explanation": demo_explanation,
                "alternatives": demo_alternatives,
                "pattern": pattern_result,
                "demo_mode": True
            })
        
        prompt = build_pattern_aware_prompt(source_code, src_lang, tgt_lang)
        logger.info(f"Translating {code_length} chars from {src_lang} to {tgt_lang}")
        
        try:
            model_output = model_client.generate(prompt)
        except Exception as e:
            logger.error(f"Model translation error: {e}")
            return jsonify({"success": False, "error": f"Translation failed: {str(e)}"}), 500
        
        try:
            parsed = parse_llm_response(model_output)
        except Exception as e:
            parsed = {"code": model_output, "explanation": "", "alternatives": ""}
        
        translated_code = parsed.get("code", "")
        
        explanation = ""
        try:
            explanation_prompt = f"Explain what this {src_lang} code does:\n\n{source_code}\n\nExplanation:"
            explanation = model_client.generate(explanation_prompt).strip()
        except Exception as e:
            logger.warning(f"Explanation error: {e}")
        
        alternatives = ""
        try:
            alternatives_prompt = f"Provide alternative implementation in {tgt_lang}:\n\n{source_code}\n\nCode:"
            alt_output = model_client.generate(alternatives_prompt)
            parsed_alt = parse_llm_response(alt_output)
            alternatives = parsed_alt.get("code", alt_output).strip()
        except Exception as e:
            logger.warning(f"Alternatives error: {e}")
        
        pattern_result = None
        try:
            pattern = detect_pattern(source_code, src_lang)
            if pattern:
                alternatives_p = map_pattern(pattern)
                pattern_result = {
                    "pattern": pattern,
                    "confidence": 0.85,
                    "alternatives": alternatives_p.get("alternatives", "") if alternatives_p else "",
                    "code_example": alternatives_p.get("code_example", "") if alternatives_p else ""
                }
        except Exception as e:
            logger.warning(f"Pattern detection error: {e}")
        
        return jsonify({
            "success": True,
            "translated_code": translated_code,
            "explanation": explanation,
            "alternatives": alternatives,
            "pattern": pattern_result
        })
    
    except Exception as e:
        logger.error(f"Translation error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/run", methods=["POST"])
def run_code():
    try:
        data = request.json
        if data is None:
            return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
        code = data.get("code")
        if not code:
            return jsonify({"success": False, "error": "Missing required field: code"}), 400
        logger.info(f"Executing code ({len(code)} chars)")
        result = execute_python(code)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": f"Execution failed: {str(e)}"}), 500


@app.route("/", methods=["GET"])
def root():
    return send_file("index.html")


@app.route("/playground", methods=["GET"])
def playground():
    return send_file("playground.html")


@app.route("/new", methods=["GET"])
def new_version():
    return send_file("index_new_v3.html")


@app.route("/final", methods=["GET"])
def final_version():
    return send_file("index_final.html")


@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"success": False, "error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    print(f"Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)

