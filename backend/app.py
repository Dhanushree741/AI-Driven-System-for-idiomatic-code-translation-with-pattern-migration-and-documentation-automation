import os
import sys
import logging
from datetime import datetime
from functools import wraps
import requests

# include workspace root on path so translator package (sitting alongside backend/) is discoverable
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
for import_path in (PROJECT_ROOT, BACKEND_DIR):
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

from translator.model_loader import HFModelClient
from translator.prompt_builder import build_translation_prompt
from translator.prompt_generator import build_pattern_aware_prompt
from translator.response_parser import parse_llm_response
from translator.module3 import parse_code, get_code_summary, detect_pattern, map_pattern
from translator.doc_service import DocumentationService
from translator.semantic_analyzer import analyze_code
from translator.complexity_estimator import estimate_complexity
from translator.doc_prompt_generator import build_prompt
from run_in_sandbox import execute_python

# Load environment variables
env_path = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Supported languages for translation
SUPPORTED_LANGUAGES = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", 
    "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala"
]

# Configuration
MAX_CODE_LENGTH = int(os.getenv("MAX_CODE_LENGTH", 10000))
PISTON_URL = os.getenv("PISTON_URL", "").strip().rstrip("/")
PLAYGROUND_LANGUAGES = {
    "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript",
    "java": "Java", "cpp": "C++", "c++": "C++", "csharp": "C#", "go": "Go", "rust": "Rust",
    "ruby": "Ruby", "php": "PHP", "swift": "Swift", "kotlin": "Kotlin", "scala": "Scala",
}

# Initialize model client
try:
    model_client = HFModelClient()
    logger.info("Model client initialized successfully")
except ValueError as e:
    logger.warning(f"Configuration Error: {e}")
    model_client = None


def require_api_key(f):
    """Decorator to require API key for protected endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_key = os.getenv("API_KEY")
        
        # If no API key is configured, allow access (for development)
        if not expected_key:
            return f(*args, **kwargs)
        
        if api_key != expected_key:
            logger.warning(f"Unauthorized access attempt from {request.remote_addr}")
            return jsonify({
                "success": False,
                "error": "Invalid or missing API key"
            }), 401
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def log_request():
    """Log all incoming requests"""
    logger.info(f"{request.method} {request.path} from {request.remote_addr}")


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "model": os.getenv("MODEL_ID"),
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/languages", methods=["GET"])
def get_supported_languages():
    """Get list of supported programming languages"""
    return jsonify({
        "success": True,
        "languages": SUPPORTED_LANGUAGES,
        "count": len(SUPPORTED_LANGUAGES)
    })


@app.route("/parse", methods=["POST"])
def parse_code_endpoint():
    """
    Parse code using Module 3 parser.
    Extracts structural information from source code.
    """
    try:
        data = request.json
        
        if data is None:
            return jsonify({
                "success": False,
                "error": "Invalid JSON payload"
            }), 400
            
        source_code = data.get("source_code")
        language = data.get("language", "Python")
        
        if not source_code:
            return jsonify({
                "success": False,
                "error": "Missing required field: source_code"
            }), 400
            
        if not isinstance(source_code, str):
            return jsonify({
                "success": False,
                "error": "source_code must be a string"
            }), 400
        
        # Parse the code using Module 3
        parse_result = parse_code(source_code, language)
        summary = get_code_summary(source_code, language)
        
        logger.info(f"Parsed {len(source_code)} chars of {language} code")
        
        return jsonify({
            "success": True,
            "parsed_result": parse_result,
            "summary": summary,
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Parse error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Parsing failed: {str(e)}"
        }), 500


@app.route("/parse/supported-languages", methods=["GET"])
def get_parser_supported_languages():
    """Get list of languages supported by the parser (Module 3)"""
    return jsonify({
        "success": True,
        "languages": [
            "Python", "JavaScript", "TypeScript", "Java", "C++", 
            "C#", "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin"
        ],
        "count": 12
    })


@app.route("/model/info", methods=["GET"])
@require_api_key
def model_info():
    """Get information about the translation model"""
    if model_client is None:
        return jsonify({
            "success": False,
            "error": "Model not initialized"
        }), 500
    
    return jsonify({
        "success": True,
        "model_id": os.getenv("MODEL_ID"),
        "supported_languages": SUPPORTED_LANGUAGES,
        "api_version": "1.0"
    })


@app.route("/translate", methods=["POST"])
def translate():
    """
    Translate code - returns translated code along with explanation, alternatives, and patterns.
    Now integrates Module 3 for analysis when model is not available.
    """
    try:
        data = request.get_json(force=True)
        
        if data is None:
            return jsonify({
                "success": False,
                "error": "Invalid JSON payload"
            }), 400
        
        source_code = data.get("source_code")
        src_lang = data.get("src_lang") or data.get("source_language", "Java")
        tgt_lang = data.get("tgt_lang") or data.get("target_language", "Python")
        
        if not source_code:
            return jsonify({
                "success": False,
                "error": "Missing required field: source_code"
            }), 400
        
        code_length = len(source_code)
        if code_length > MAX_CODE_LENGTH:
            return jsonify({
                "success": False,
                "error": f"Source code exceeds maximum length of {MAX_CODE_LENGTH} characters"
            }), 400
        
        # DEBUG: Print what we're processing
        print(f"\n=== DEBUG: translate() called ===")
        print(f"Source code length: {code_length}")
        print(f"Source language: {src_lang}")
        print(f"Target language: {tgt_lang}")
        print(f"Model client available: {model_client is not None}")
        
        # Check if model is available
        if model_client is None:
            # DEBUG
            print("DEBUG: Model client not available, using Module 3 fallback")
            
            # Use Module 3 to generate analysis
            module3_result = None
            try:
                print(f"DEBUG: Calling parse_code() for {src_lang}")
                module3_result = parse_code(source_code, src_lang, tgt_lang)
                print(f"DEBUG: parse_code() returned successfully")
            except Exception as e:
                print(f"DEBUG: parse_code() error: {e}")
                logger.error(f"Module 3 parse error: {e}")
            
            # Generate demo translation based on simple patterns
            demo_translation = source_code
            
            # Extract explanation from Module 3 if available
            demo_explanation = module3_result.get("explanation", "") if module3_result else ""
            if not demo_explanation:
                demo_explanation = f"This is a {src_lang} code snippet that would be translated to {tgt_lang}. To enable real translation, please configure your HuggingFace API key in the .env file."
            
            # Extract alternatives from Module 3
            demo_alternatives = module3_result.get("alternative", []) if module3_result else []
            if demo_alternatives:
                # Format alternatives as string
                demo_alternatives_str = "\n\n".join([
                    f"## {alt.get('name', 'Alternative')}\n{alt.get('code', '')}" 
                    for alt in demo_alternatives if alt.get('code')
                ])
            else:
                demo_alternatives_str = source_code
            
            # Extract patterns from Module 3
            pattern_result = None
            if module3_result and module3_result.get("pattern", {}).get("detected"):
                pattern_data = module3_result.get("pattern", {})
                pattern_result = {
                    "pattern": pattern_data.get("detected"),
                    "confidence": pattern_data.get("confidence", 0.85),
                    "all_patterns": pattern_data.get("all_patterns", [])
                }
                print(f"DEBUG: Pattern detected: {pattern_result}")
            
            print(f"=== END DEBUG ===\n")
            
            return jsonify({
                "success": True,
                "translated_code": demo_translation,
                "explanation": demo_explanation,
                "alternatives": demo_alternatives_str,
                "pattern": pattern_result,
                "module3_result": module3_result,
                "demo_mode": True
            })
        
        # Use pattern-aware prompt for translation
        prompt = build_pattern_aware_prompt(source_code, src_lang, tgt_lang)
        
        logger.info(f"Translating {code_length} chars from {src_lang} to {tgt_lang}")
        print(f"\n=== DEBUG: Calling model ===")
        print(f"PROMPT SENT TO MODEL:\n{prompt[:500]}...")
        
        # LLM translation
        translated_code = source_code
        try:
            model_output = model_client.generate(prompt)
            print(f"MODEL RESPONSE:\n{model_output[:500]}...")
            
            # Parse response to get clean code
            parsed = parse_llm_response(model_output)
            translated_code = parsed.get("code", source_code)
        except Exception as e:
            logger.error(f"Model translation error: {e}")
            print(f"DEBUG: Model error: {e}")
            message = str(e)
            if "model_not_supported" in message or "not supported by any provider" in message:
                message = (
                    f"The configured Hugging Face model '{os.getenv('MODEL_ID')}' is not available "
                    "through your enabled Inference Providers. Choose a model listed at "
                    "https://huggingface.co/inference/models or enable a provider for this model, "
                    "then restart the backend."
                )
            return jsonify({"success": False, "error": message}), 502
        # Get Module 3 analysis on the TRANSLATED code (not source code)
        print("DEBUG: Getting Module 3 analysis on translated code...")
        module3_result = None
        try:
            # Parse the translated code with target language
            module3_result = parse_code(translated_code, tgt_lang)
            print(f"DEBUG: Module 3 result obtained for translated code")
        except Exception as e:
            print(f"DEBUG: Module 3 error on translated code: {e}")
            # Fallback: try with source code
            try:
                module3_result = parse_code(source_code, src_lang)
            except Exception as e2:
                print(f"DEBUG: Module 3 fallback also failed: {e2}")
        
        # Use Module 3 results as primary source
        explanation = ""
        if module3_result and module3_result.get("explanation"):
            explanation = module3_result.get("explanation", "")
            print("DEBUG: Using Module 3 explanation")
        
        # Use Module 3 alternatives
        alternatives = ""
        if module3_result and module3_result.get("alternative"):
            alt_list = module3_result.get("alternative", [])
            alternatives = "\n\n".join([
                f"## {alt.get('name', 'Alternative')}\n{alt.get('code', '')}" 
                for alt in alt_list if alt.get('code')
            ])
            print("DEBUG: Using Module 3 alternatives")
        
        # Get pattern detection using Module 3
        pattern_result = None
        if module3_result and module3_result.get("pattern"):
            pattern_data = module3_result.get("pattern", {})
            detected = pattern_data.get("detected")
            
            if detected:
                pattern_result = {
                    "pattern": detected,
                    "confidence": pattern_data.get("confidence", 0.85),
                    "all_patterns": pattern_data.get("all_patterns", [])
                }
            else:
                # Show message even when no pattern detected
                structure = module3_result.get("structure", {})
                pattern_result = {
                    "pattern": "No design pattern detected",
                    "confidence": 0.0,
                    "all_patterns": [],
                    "message": f"This is a simple {structure.get('function_count', 0)}-function, {structure.get('class_count', 0)}-class code snippet. Consider using patterns like Singleton, Factory, or Observer for larger applications."
                }
            print(f"DEBUG: Pattern from Module 3: {pattern_result}")
        
        print(f"=== END DEBUG ===\n")
        
        return jsonify({
            "success": True,
            "translated_code": translated_code,
            "explanation": explanation,
            "alternatives": alternatives,
            "pattern": pattern_result,
            "module3_result": module3_result
        })
    
    except Exception as e:
        logger.error(f"Translation error: {e}", exc_info=True)
        print(f"DEBUG: Final error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Get explanation and alternatives for translated code.
    """
    try:
        data = request.get_json(force=True)
        
        if data is None:
            return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
        
        source_code = data.get("source_code")
        src_lang = data.get("source_lang") or data.get("source_language", "Python")
        tgt_lang = data.get("tgt_lang") or data.get("target_language", "JavaScript")
        
        if not source_code:
            return jsonify({"success": False, "error": "Missing required field: source_code"}), 400
        
        if model_client is None:
            return jsonify({"success": False, "error": "Model client not initialized"}), 500
        
        # First get the translation
        translate_prompt = build_translation_prompt(source_code, src_lang, tgt_lang)
        try:
            translated = model_client.generate(translate_prompt)
            parsed = parse_llm_response(translated)
            translated_code = parsed.get("code", translated)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            translated_code = str(e)
        
        # Then get explanation
        explanation_prompt = f"""Explain what this {src_lang} code does in simple terms:

{source_code}

Explanation:"""
        
        try:
            explanation = model_client.generate(explanation_prompt)
            # Clean up the response
            explanation = explanation.strip()
        except Exception as e:
            explanation = f"Error: {str(e)}"
        
        # Get alternatives
        alternatives_prompt = f"""Provide an alternative implementation of this code in {tgt_lang}:

{source_code}

Alternative {tgt_lang} code:"""
        
        try:
            alternatives = model_client.generate(alternatives_prompt)
            # Parse to get clean code
            parsed_alt = parse_llm_response(alternatives)
            alternatives = parsed_alt.get("code", alternatives)
        except Exception as e:
            alternatives = f"Error: {str(e)}"
        
        return jsonify({
            "success": True,
            "translated_code": translated_code,
            "explanation": explanation,
            "alternatives": alternatives
        })
    
    except Exception as e:
        logger.error(f"Analyze error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500



@app.route("/documentation", methods=["POST"])
def generate_documentation():
    """
    Generate documentation for the source code using Module 4 (Documentation Service).
    """
    try:
        data = request.get_json(force=True)
        
        if data is None:
            return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
        
        source_code = data.get("source_code")
        
        if not source_code:
            return jsonify({"success": False, "error": "Missing required field: source_code"}), 400
        
        if model_client is None:
            return jsonify({"success": False, "error": "Model client not initialized"}), 500
        
        # Import the doc service functions
        from translator.semantic_analyzer import analyze_code
        from translator.complexity_estimator import estimate_complexity
        from translator.doc_prompt_generator import build_prompt
        
        # Get semantic analysis
        semantic_data = analyze_code(source_code)
        
        # Get complexity estimate
        complexity = estimate_complexity(source_code)
        
        # Build documentation prompt
        doc_prompt = build_prompt(source_code, semantic_data, complexity)
        
        # Generate documentation
        try:
            documentation = model_client.generate(doc_prompt)
            documentation = documentation.strip()
        except Exception as e:
            logger.error(f"Documentation generation error: {e}")
            documentation = f"Error: {str(e)}"
        
        return jsonify({
            "success": True,
            "documentation": documentation,
            "complexity": complexity,
            "structure": semantic_data
        })
    
    except Exception as e:
        logger.error(f"Documentation error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/generate-docs", methods=["POST"])
def generate_docs():
    """
    Generate documentation using the doc_service module.
    """
    try:
        data = request.json
        
        if data is None:
            return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
            
        code = data.get("source_code")
        
        if not code:
            return jsonify({"success": False, "error": "Missing required field: source_code"}), 400
        
        # Use the doc_service to generate documentation
        result = DocumentationService.generate_docs(code)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Generate docs error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Documentation generation failed: {str(e)}"
        }), 500


@app.route("/run", methods=["POST"])
def run_code():
    """Execute code in the configured sandbox, or use the local Python runner."""
    try:
        data = request.json
        
        if data is None:
            return jsonify({
                "success": False,
                "error": "Invalid JSON payload"
            }), 400
            
        code = data.get("code")
        language = str(data.get("language", "python")).strip().lower()
        version = str(data.get("version", "*")).strip() or "*"
        stdin = data.get("stdin", "")
        
        if not code:
            return jsonify({
                "success": False,
                "error": "Missing required field: code"
            }), 400
            
        if not isinstance(code, str):
            return jsonify({
                "success": False,
                "error": "code must be a string"
            }), 400

        if not isinstance(stdin, str):
            return jsonify({"success": False, "error": "stdin must be a string"}), 400
        if len(stdin) > MAX_CODE_LENGTH:
            return jsonify({"success": False, "error": f"Standard input exceeds the {MAX_CODE_LENGTH} character limit"}), 413
        if len(code) > MAX_CODE_LENGTH:
            return jsonify({"success": False, "error": f"Code exceeds the {MAX_CODE_LENGTH} character limit"}), 413
        if PISTON_URL:
            runtime_response = requests.get(f"{PISTON_URL}/api/v2/runtimes", timeout=5)
            runtime_response.raise_for_status()
            if not any(
                str(runtime.get("language", "")).lower() == language
                and (version == "*" or str(runtime.get("version", "")) == version)
                for runtime in runtime_response.json()
            ):
                return jsonify({"success": False, "error": "That language runtime is not installed"}), 400
        elif language != "python":
            return jsonify({"success": False, "error": "Multi-language execution is not configured. Set PISTON_URL to a self-hosted Piston service."}), 503
            
        logger.info("Executing %s code (%s chars)", language, len(code))
        if PISTON_URL:
            response = requests.post(
                f"{PISTON_URL}/api/v2/execute",
                json={
                    "language": language,
                    "version": version,
                    "files": [{"content": code}],
                    "stdin": stdin,
                    "run_timeout": 5000,
                    "compile_timeout": 10000,
                },
                timeout=20,
            )
            response.raise_for_status()
            piston_result = response.json()
            run_result = piston_result.get("run") or {}
            compile_result = piston_result.get("compile") or {}
            result = {
                "stdout": run_result.get("stdout", ""),
                "stderr": "\n".join(part for part in [compile_result.get("stderr", ""), run_result.get("stderr", "")] if part),
                "returncode": run_result.get("code", compile_result.get("code", 0)),
                "language": piston_result.get("language", language),
                "version": piston_result.get("version", version),
            }
        elif language == "python" and os.getenv("VERCEL") != "1":
            result = execute_python(code, stdin=stdin)
        else:
            return jsonify({
                "success": False,
                "error": "Code execution is disabled on deployment unless PISTON_URL is configured to use an isolated execution service.",
            }), 503
        
        return jsonify({
            "success": True,
            "result": result
        })
        
    except requests.RequestException as e:
        logger.error("Execution service error: %s", e)
        return jsonify({"success": False, "error": "Execution service is unavailable or rejected the request"}), 502
    except Exception as e:
        logger.error(f"Execution error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Execution failed: {str(e)}"
        }), 500


@app.route("/runtimes", methods=["GET"])
def get_playground_runtimes():
    """Return installed Piston runtimes, or Python when using the local fallback."""
    if not PISTON_URL:
        return jsonify({"success": True, "runtimes": [{"language": "python", "display_name": "Python", "version": "local"}]})
    try:
        response = requests.get(f"{PISTON_URL}/api/v2/runtimes", timeout=5)
        response.raise_for_status()
        runtimes = []
        for runtime in response.json():
            runtime_id = str(runtime.get("language", "")).lower()
            if runtime_id:
                runtimes.append({
                    "language": runtime_id,
                    "display_name": PLAYGROUND_LANGUAGES.get(runtime_id, runtime_id.replace(".", " ").title()),
                    "version": runtime.get("version", "*"),
                })
        return jsonify({"success": True, "runtimes": runtimes})
    except (requests.RequestException, ValueError) as e:
        logger.error("Unable to load Piston runtimes: %s", e)
        return jsonify({"success": False, "error": "Could not load execution runtimes"}), 502


@app.route("/", methods=["GET"])
def root():
    """Serve the main application with translation and playground"""
    return send_file(os.path.join(BACKEND_DIR, "index_new_v3.html"))


@app.route("/playground", methods=["GET"])
def playground():
    """Serve the playground HTML"""
    return send_file(os.path.join(BACKEND_DIR, "playground.html"))


@app.route("/live", methods=["GET"])
def live_playground():
    """Serve the live translator with playground"""
    return send_file(os.path.join(BACKEND_DIR, "index_live.html"))


@app.route("/new", methods=["GET"])
def new_version():
    """Serve the new version with highlight tabs"""
    return send_file(os.path.join(BACKEND_DIR, "index_new_v3.html"))


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    
    try:
        logger.info(f"Starting Flask server on port {port}...")
        print(f"Starting Flask server on port {port}...")
        app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
    except KeyboardInterrupt:
        logger.info("Shutting down Flask server...")
        print("\nShutting down Flask server...")
    except Exception as e:
        logger.error(f"Error starting Flask app: {e}")
        print(f"Error starting Flask app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)




