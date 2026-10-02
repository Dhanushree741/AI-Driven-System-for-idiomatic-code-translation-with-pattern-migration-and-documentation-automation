import re
import json


def extract_json(text):
    """
    Safely extract JSON from model response.
    Handles cases where model returns text before/after JSON.
    """
    if not text:
        return None
    
    # Try to find JSON object in the text
    # Match {...} with potential newlines inside
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    match = re.search(json_pattern, text, re.DOTALL)
    
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    
    # Try direct JSON parse if text starts with {
    if text.strip().startswith('{'):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    
    return None


def parse_llm_response(response):
    """
    Parse LLM response to extract translated code, explanation, alternatives, and patterns.
    Now supports structured JSON output.
    """
    
    # First, try to extract JSON from the response
    json_data = extract_json(response)
    
    if json_data:
        return {
            "code": json_data.get("translated_code", ""),
            "explanation": json_data.get("explanation", ""),
            "alternatives": json_data.get("alternatives", []),
            "patterns": json_data.get("patterns", [])
        }
    
    # Fallback to original code block extraction
    # If response contains markdown code blocks, extract the code inside
    if "```" in response:
        # Find code blocks (```language ... ```)
        code_blocks = re.findall(r'```(?:\w+)?\n?(.*?)```', response, re.DOTALL)
        if code_blocks:
            # Take the first code block as the main translation
            code = code_blocks[0].strip()
            return {
                "code": code,
                "explanation": "",
                "alternatives": [],
                "patterns": []
            }
    
    # If no code blocks, clean up the response directly
    code = response.strip()
    
    # Remove any leading markers
    code = code.replace("### Translated Code", "").replace("### Code", "")
    code = code.replace("Translated Code:", "").replace("Code:", "")
    
    return {
        "code": code,
        "explanation": "",
        "alternatives": [],
        "patterns": []
    }


from .module3 import parse_code, get_code_summary


def build_translation_prompt(source_code, src_lang, tgt_lang, include_analysis=True):
    """
    Builds a clean translation prompt for Code Llama / Qwen.
    Now integrates Module 3 (Parser) for code analysis.
    """
    
    prompt = f"""Convert this {src_lang} code to {tgt_lang}.
Output ONLY raw code - no markdown, no explanations, no comments.
Start directly with the code.

{source_code}

```{tgt_lang}
"""

    return prompt.strip()

