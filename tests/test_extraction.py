import json
import os
import sys

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_inference() -> None:
    # Check if any model is available
    status_res = client.get("/status")
    status_data = status_res.json()

    if not status_data["available_models"]:
        print("No models available. Skipping test.")
        return

    model_name = status_data["available_models"][0]

    # Load model if not loaded
    if status_data["loaded_model"] != model_name:
        client.post("/load", json={"model_name": model_name})

    payload = {
        "prompt": "Extract name and age from: John is 30 years old.",
        "config": {"temperature": 0.0, "max_tokens": 100},
        "schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
            "required": ["name", "age"],
        },
    }

    print(f"Sending request to /inference with model {model_name}...")
    response = client.post("/inference", json=payload)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)

    assert response.status_code == 200
    data = response.json()
    print("Response received:")
    print(json.dumps(data, indent=2))

    result = data["result"]
    assert result["name"] == "John"
    assert result["age"] == 30
    print("Test passed!")


if __name__ == "__main__":
    test_inference()
