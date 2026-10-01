# translator/app.py - Main translation application
# Module 3: Parser Integration

from .model_loader import HFModelClient
from .prompt_builder import build_translation_prompt
from .parser import parse_code, get_code_summary, CodeParser

# Initialize parser
parser = CodeParser()


def translate_with_parsing(source_code, src_lang, tgt_lang, use_parser=True):
    """
    Translate code with optional parsing analysis.
    
    Args:
        source_code: Source code to translate
        src_lang: Source language
        tgt_lang: Target language
        use_parser: Whether to use the parser for analysis
        
    Returns:
        Dictionary with translation and analysis results
    """
    # Module 3: Parse the source code
    parse_result = None
    code_summary = None
    
    if use_parser:
        try:
            parse_result = parse_code(source_code, src_lang)
            code_summary = get_code_summary(source_code, src_lang)
        except Exception as e:
            parse_result = {"error": str(e)}
    
    # Build the translation prompt
    prompt = build_translation_prompt(source_code, src_lang, tgt_lang)
    
    # Translate using the model
    try:
        model_client = HFModelClient()
        translated_code = model_client.generate(prompt)
        
        return {
            "success": True,
            "source_code": source_code,
            "translated_code": translated_code,
            "source_language": src_lang,
            "target_language": tgt_lang,
            "parse_result": parse_result,
            "code_summary": code_summary
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "parse_result": parse_result
        }


# Simple translation function
def translate(source_code, src_lang, tgt_lang, prompt_override=None):
    """
    Simple translation without parsing.
    """
    if prompt_override:
        prompt = prompt_override
    else:
        prompt = build_translation_prompt(source_code, src_lang, tgt_lang)
    
    try:
        model_client = HFModelClient()
        translated_code = model_client.generate(prompt)
        return translated_code
    except Exception as e:
        raise Exception(f"Translation failed: {str(e)}")


# Legacy function for backward compatibility
def detect_pattern(source_code, language):
    """Legacy pattern detection - uses ast_parser."""
    from .ast_parser import parse_python, parse_java
    
    if language.lower() == "python":
        tree = parse_python(source_code)
        if isinstance(tree, dict):
            return {"pattern": "Unknown", "confidence": 0.0}
        return {"pattern": "Unknown", "confidence": 0.2}
    elif language.lower() == "java":
        struct = parse_java(source_code)
        return {"pattern": "Unknown", "confidence": 0.2}
    
    return {"pattern": "Unknown", "confidence": 0.0}


def map_pattern(pattern, src_lang, tgt_lang):
    """Legacy pattern mapping."""
    return {
        "strategy": "direct_translation",
        "description": "No pattern detected.",
        "best_practices": [],
        "alternatives": []
    }


def build_pattern_aware_prompt(source_code, src_lang, tgt_lang, pattern_info, mapping_info):
    """Legacy prompt builder."""
    from .prompt_generator import build_pattern_aware_prompt as build_prompt
    return build_prompt(source_code, src_lang, tgt_lang, pattern_info, mapping_info)

