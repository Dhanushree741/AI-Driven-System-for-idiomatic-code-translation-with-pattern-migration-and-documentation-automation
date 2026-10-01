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
