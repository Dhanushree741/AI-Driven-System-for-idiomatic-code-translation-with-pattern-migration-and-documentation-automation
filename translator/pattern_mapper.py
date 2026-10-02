def map_pattern(pattern_info, src_lang, tgt_lang):

    pattern = pattern_info.get("pattern")

    mapping = {}

    if pattern == "Singleton":

        mapping = {
            "strategy": "module_level_singleton",
            "description": "Convert Java singleton to Python module-level instance",
            "best_practices": [
                "Avoid unnecessary singleton in Python",
                "Use lazy initialization if required"
            ],
            "alternatives": [
                "Decorator Singleton",
                "Borg Pattern"
            ]
        }

    elif pattern == "Factory":

        mapping = {
            "strategy": "factory_function",
            "description": "Use Python factory function instead of class factory",
            "best_practices": [
                "Use dynamic typing",
                "Return appropriate subclass"
            ],
            "alternatives": [
                "Dictionary-based factory",
                "Class registry"
            ]
        }

    elif pattern == "Observer":

        mapping = {
            "strategy": "event_listener",
            "description": "Convert Java observer to Python event listener pattern",
            "best_practices": [
                "Use callback functions",
                "Keep observer loosely coupled"
            ],
            "alternatives": [
                "Async event system",
                "Pub-Sub pattern"
            ]
        }

    elif pattern == "Adapter":

        mapping = {
            "strategy": "wrapper_class",
            "description": "Use wrapper class to adapt interface",
            "best_practices": [
                "Keep adapter lightweight",
                "Avoid modifying original class"
            ],
            "alternatives": [
                "Composition adapter",
                "Inheritance adapter"
            ]
        }

    else:

        mapping = {
            "strategy": "direct_translation",
            "description": "No pattern detected",
            "best_practices": [],
            "alternatives": []
        }

    return mapping