from .semantic_analyzer import analyze_code
from .complexity_estimator import estimate_complexity
from .doc_prompt_generator import build_prompt

class DocumentationService:

    def __init__(self, translator):
        self.translator = translator

    def generate_docs(self, code):

        semantic_data = analyze_code(code)

        complexity = estimate_complexity(code)

        prompt = build_prompt(
            code,
            semantic_data,
            complexity
        )

        documentation = self.translator.chat(prompt)

        return {
            "documentation": documentation,
            "complexity": complexity,
            "structure": semantic_data
        }
