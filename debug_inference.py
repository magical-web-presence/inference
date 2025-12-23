import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.inference import ModelManager


def test_inference() -> None:
    manager = ModelManager()
    models = manager.list_models()
    if not models:
        print("No models found")
        return

    print(f"Loading model: {models[0]}")
    manager.load_model(models[0], n_ctx=2048)

    print("\nTesting updated generate method (Thinking DISABLED):")
    result = manager.generate("Hello, who are you?", {"max_tokens": 50, "thinking": False})
    print(f"Result: {result}")

    print("\nTesting updated generate method (Thinking ENABLED):")
    result = manager.generate("Hello, who are you?", {"max_tokens": 50, "thinking": True})
    print(f"Result: {result}")

    print("\nTesting updated generate method (Grammar Extraction):")
    schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}, "required": ["name", "age"]}
    result = manager.generate("Extract name and age: John Doe is 30 years old.", {"max_tokens": 50}, schema)
    print(f"Result: {result}")


if __name__ == "__main__":
    test_inference()
