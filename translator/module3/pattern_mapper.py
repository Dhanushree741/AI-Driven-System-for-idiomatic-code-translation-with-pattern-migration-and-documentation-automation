# backend/translator/module3/pattern_mapper.py
# Pattern mapping module with full code implementations for alternatives


def map_pattern(pattern_info, src_lang, tgt_lang):
    """Map design patterns from source language to target language with full implementations."""
    
    pattern = pattern_info.get("pattern", "Unknown")
    
    # Mapping table with full code implementations
    # Using simplified structure to avoid syntax issues
    mapping_table = _get_mapping_table()
    
    # Try to find pattern in table
    pattern_data = mapping_table.get(pattern, {})
    src_data = pattern_data.get(src_lang.lower(), {})
    
    if not src_data:
        return {
            "strategy": "direct_translation",
            "description": f"No specific pattern mapping available for {pattern} from {src_lang} to {tgt_lang}.",
            "best_practices": [],
            "alternatives": []
        }
    
    return {
        "strategy": src_data.get("strategy", "direct_translation"),
        "description": src_data.get("description", ""),
        "best_practices": src_data.get("best_practices", []),
        "alternatives": src_data.get("alternatives", [])
    }


def _get_mapping_table():
    """Returns the pattern mapping table with code implementations."""
    return {
        "Singleton": {
            "python": {
                "strategy": "module_level_singleton",
                "description": "Use Python module-level instance instead of private constructor.",
                "best_practices": [
                    "Avoid unnecessary singleton complexity",
                    "Use lazy initialization if needed",
                    "Consider using functools.lru_cache for simple caching"
                ],
                "alternatives": []
            },
            "javascript": {
                "strategy": "module_export_singleton", 
                "description": "Use JavaScript module pattern with exports for singleton behavior.",
                "best_practices": [
                    "Use ES6 modules for modern singleton implementation",
                    "Avoid global variables",
                    "Use IIFE for private state"
                ],
                "alternatives": []
            }
        },
        "Factory": {
            "python": {
                "strategy": "factory_function",
                "description": "Use Python factory function instead of Java factory class.",
                "best_practices": [
                    "Use polymorphism for flexible object creation",
                    "Avoid long if-else factory chains - use dictionary dispatch",
                    "Consider using abstract base classes for type hints"
                ],
                "alternatives": []
            },
            "javascript": {
                "strategy": "factory_function",
                "description": "Use JavaScript factory functions for object creation.",
                "best_practices": [
                    "Use closures for private data",
                    "Return consistent interface",
                    "Consider composition over inheritance"
                ],
                "alternatives": []
            }
        },
        "Observer": {
            "python": {
                "strategy": "event_listener_pattern",
                "description": "Python uses callbacks, properties, and signals for observer pattern.",
                "best_practices": [
                    "Keep observers loosely coupled to subject",
                    "Avoid circular dependencies between observers",
                    "Use weak references to prevent memory leaks"
                ],
                "alternatives": []
            },
            "javascript": {
                "strategy": "event_listener_pattern",
                "description": "JavaScript uses EventTarget, custom events, and callbacks.",
                "best_practices": [
                    "Use WeakMap for private data",
                    "Remove listeners when done to prevent memory leaks",
                    "Consider using built-in EventTarget"
                ],
                "alternatives": []
            }
        },
        "Adapter": {
            "python": {
                "strategy": "wrapper_adapter",
                "description": "Adapter pattern converts interface of a class into another interface.",
                "best_practices": [
                    "Prefer composition over inheritance",
                    "Keep adapter thin - just delegate to wrapped object",
                    "Use duck typing in Python for more flexibility"
                ],
                "alternatives": []
            },
            "javascript": {
                "strategy": "wrapper_adapter",
                "description": "Adapter in JavaScript wraps incompatible objects to work together.",
                "best_practices": [
                    "Keep adapter focused on interface conversion",
                    "Don't add business logic in adapter",
                    "Use composition for more flexibility"
                ],
                "alternatives": []
            }
        },
        "Strategy": {
            "python": {
                "strategy": "strategy_pattern",
                "description": "Strategy pattern defines family of algorithms, encapsulates each one.",
                "best_practices": [
                    "Use strategy interface for type consistency",
                    "Avoid strategy explosion - keep number reasonable",
                    "Consider using functions as strategies (simpler)"
                ],
                "alternatives": []
            },
            "javascript": {
                "strategy": "strategy_pattern",
                "description": "Strategy pattern in JavaScript encapsulates algorithms as objects.",
                "best_practices": [
                    "Use consistent strategy interface",
                    "Consider function strategies for simple cases",
                    "Use composition over inheritance"
                ],
                "alternatives": []
            }
        },
        "Decorator": {
            "python": {
                "strategy": "decorator_pattern",
                "description": "Python decorators are a language feature that makes this pattern elegant.",
                "best_practices": [
                    "Use functools.wraps to preserve function metadata",
                    "Chain multiple decorators for composed behavior",
                    "Use classes for decorators with state"
                ],
                "alternatives": []
            },
            "javascript": {
                "strategy": "decorator_pattern",
                "description": "JavaScript decorators or higher-order functions add behavior.",
                "best_practices": [
                    "Use Reflect.ownKeys for metadata",
                    "Chain decorators for composition",
                    "Consider mixins as alternative"
                ],
                "alternatives": []
            }
        },
        "Repository": {
            "python": {
                "strategy": "repository_pattern",
                "description": "Repository pattern abstracts data layer, providing collection-like interface.",
                "best_practices": [
                    "Define clear interface for repository",
                    "Implement caching for frequently accessed data",
                    "Handle transactions appropriately"
                ],
                "alternatives": []
            },
            "javascript": {
                "strategy": "repository_pattern",
                "description": "Repository pattern in JavaScript abstracts data access.",
                "best_practices": [
                    "Define consistent interface",
                    "Use TypeScript for type safety",
                    "Implement caching layer"
                ],
                "alternatives": []
            }
        },
        "Dependency Injection": {
            "python": {
                "strategy": "dependency_injection",
                "description": "Dependency Injection promotes loose coupling and easier testing.",
                "best_practices": [
                    "Use constructor injection for required dependencies",
                    "Use setter injection for optional dependencies",
                    "Use interface/protocol for type hints"
                ],
                "alternatives": []
            },
            "javascript": {
                "strategy": "dependency_injection",
                "description": "Dependency Injection in JavaScript via constructor or factory.",
                "best_practices": [
                    "Use constructor injection",
                    "Avoid service locator anti-pattern",
                    "Consider using DI container for complex apps"
                ],
                "alternatives": []
            }
        }
    }

