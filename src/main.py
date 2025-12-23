import os
import json
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path

# Ensure the parent directory is in sys.path so 'src' can be imported
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.inference import ModelManager

app = FastAPI(title="Qwen3 API Service")
manager = ModelManager()

# Create static directory if it doesn't exist
static_dir = Path(root_dir) / "static"
static_dir.mkdir(exist_ok=True)


class LoadModelRequest(BaseModel):
    model_name: str
    n_ctx: Optional[int] = 32768
    n_gpu_layers: Optional[int] = -1


@app.get("/", response_class=HTMLResponse)
async def get_index() -> str:
    index_path = static_dir / "index.html"
    if index_path.exists():
        return index_path.read_text()
    return "<h1>Qwen3 API Service</h1><p>Testing UI not found. Please create static/index.html</p>"


@app.get("/status")
async def get_status() -> Dict[str, Any]:
    return manager.get_status()


@app.post("/load")
async def load_model(request: LoadModelRequest) -> Dict[str, str]:
    try:
        n_ctx_val = int(request.n_ctx or 32768)
        n_gpu_layers_val = int(request.n_gpu_layers or -1)
        manager.load_model(request.model_name, n_ctx_val, n_gpu_layers_val)
        return {"status": "success", "message": f"Model {request.model_name} loaded"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")


@app.post("/unload")
async def unload_model() -> Dict[str, str]:
    manager.unload_model()
    return {"status": "success", "message": "Model unloaded"}


@app.post("/inference")
async def inference(request: Request) -> Dict[str, Any]:
    try:
        body = await request.json()
        prompt = body.get("prompt")
        if not prompt:
            raise HTTPException(status_code=400, detail="Missing prompt in request body")
        cfg = body.get("config") or {}
        schema = body.get("schema")
        result = manager.generate(prompt, cfg, schema)
        return {"status": "success", "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Try to load the first available model on startup
    models = manager.list_models()
    if models:
        try:
            manager.load_model(models[0])
            print(f"Auto-loaded model: {models[0]}")
        except Exception as e:
            print(f"Failed to auto-load model: {e}")

    uvicorn.run(app, host="0.0.0.0", port=9000)
