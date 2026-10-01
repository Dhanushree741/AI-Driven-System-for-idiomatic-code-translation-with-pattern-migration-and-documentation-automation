def format_list(items):

    if not items:
        return "- None"

    return "\n".join([f"- {i}" for i in items])


def build_pattern_aware_prompt(
    source_code,
    src_lang,
    tgt_lang,
    pattern_info=None,
    mapping_info=None
):
    """
    Build a pattern-aware prompt that requests structured JSON output
    including explanation, alternatives, and detected patterns.
    """
    
    prompt = f"""You are an expert software engineer.

Analyze and translate this {src_lang} code to {tgt_lang}.

Return your response as a JSON object with these fields:
{{
 "translated_code": "the translated code only, no markdown fences",
 "explanation": "clear explanation of what the code does",
 "alternatives": ["alternative implementation 1", "alternative implementation 2"],
 "patterns": ["detected design pattern if any, or empty array"]
}}

Code to translate:
{source_code}

JSON Response:"""

    return prompt

