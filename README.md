# Qwen3 API Service

This project provides a simplified API service for Qwen3 models with support for dynamic model loading/unloading, JSON Schema (grammar-restricted decoding), and a built-in testing UI.

## Features
- **Dynamic Model Management**: Load and unload models via API endpoints.
- **Inference API**: Simple endpoint for prompt-based inference with custom config and schema.
- **JSON Schema Support**: Enforce structured output using JSON Schema.
- **Testing UI**: Built-in HTML page for easy testing and interaction.
- **Optimized**: Uses `llama-cpp-python` for efficient inference.

## Usage

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download Model**:
   ```bash
   python src/downloader.py
   ```

3. **Start Server**:
   ```bash
   python src/main.py
   ```

4. **Access Testing UI**:
   Open `http://localhost:8000` in your browser.

## API Endpoints

### `GET /status`
Returns the currently loaded model and a list of available models.

### `POST /load`
Loads a specific model.
```json
{
  "model_name": "Qwen3-8B-Q8_0.gguf",
  "n_ctx": 32768,
  "n_gpu_layers": -1
}
```

### `POST /unload`
Unloads the current model to free up memory.

### `POST /inference`
Performs inference.
```json
{
  "prompt": "Extract name and age from: John is 30 years old.",
  "config": {
    "temperature": 0.7,
    "max_tokens": 512
  },
  "schema": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "age": {"type": "integer"}
    },
    "required": ["name", "age"]
  }
}
```

## Architecture
- `src/downloader.py`: Handles model acquisition.
- `src/inference.py`: `ModelManager` class for loading/unloading and generation.
- `src/main.py`: FastAPI server and API endpoints.
- `static/index.html`: Testing UI.
