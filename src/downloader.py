import os
import requests
import hashlib
import argparse
from typing import Optional
from tqdm import tqdm

MODELS = {"8b": {"url": "https://huggingface.co/Qwen/Qwen3-8B-GGUF/resolve/main/Qwen3-8B-Q8_0.gguf?download=true", "path": "models/Qwen3-8B-Q8_0.gguf"}, "4b": {"url": "https://huggingface.co/Qwen/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q8_0.gguf?download=true", "path": "models/Qwen3-4B-Q8_0.gguf"}}


def download_model(url: str, dest_path: str, force: bool = False) -> None:
    if os.path.exists(dest_path) and not force:
        print(f"Model already exists at {dest_path}. Use --force to re-download.")
        return

    print(f"Downloading model from {url}...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, "wb") as f, tqdm(
        desc=dest_path,
        total=total_size,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            bar.update(size)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Qwen3 models")
    parser.add_argument("--model", type=str, choices=["4b", "8b", "all"], default="8b", help="Model to download")
    parser.add_argument("--force", action="store_true", help="Force re-download")
    args = parser.parse_args()

    if args.model == "all":
        for m in MODELS.values():
            download_model(m["url"], m["path"], args.force)
    else:
        m = MODELS[args.model]
        download_model(m["url"], m["path"], args.force)
