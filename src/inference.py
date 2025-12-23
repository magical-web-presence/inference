import json
import os
import threading
from typing import Any, Dict, List, Optional, Union, cast
from llama_cpp import Llama
from llama_cpp.llama_grammar import LlamaGrammar


class ModelManager:
    def __init__(self, models_dir: str = "models") -> None:
        self.models_dir = models_dir
        self.current_model: Optional[Llama] = None
        self.current_model_name: Optional[str] = None
        # lock to serialize access to the underlying llama context (not thread-safe)
        self._lock = threading.RLock()

    def list_models(self) -> List[str]:
        if not os.path.exists(self.models_dir):
            return []
        return [f for f in os.listdir(self.models_dir) if f.endswith(".gguf")]

    def load_model(self, model_name: str, n_ctx: int = 4096, n_gpu_layers: int = -1) -> bool:
        with self._lock:
            if self.current_model_name == model_name:
                return True

            model_path = os.path.join(self.models_dir, model_name)
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model {model_name} not found in {self.models_dir}")

            print(f"Attempting to load model: {model_path}")
            # ensure previous model is unloaded under lock
            self.unload_model()

            try:
                self.current_model = Llama(model_path=model_path, n_ctx=n_ctx, n_gpu_layers=n_gpu_layers, verbose=False, chat_format="qwen")
                self.current_model_name = model_name
                print(f"Successfully loaded {model_name}")
                return True
            except Exception as e:
                print(f"Error loading model {model_name}: {e}")
                self.unload_model()
                raise e

    def unload_model(self) -> None:
        with self._lock:
            if self.current_model:
                print(f"Unloading model: {self.current_model_name}")
                try:
                    # Explicitly close to avoid __del__ issues
                    if hasattr(self.current_model, "close"):
                        self.current_model.close()
                except Exception as e:
                    print(f"Error during model close: {e}")

                try:
                    del self.current_model
                except Exception:
                    pass
                self.current_model = None
                self.current_model_name = None
                import gc

                gc.collect()

    def get_status(self) -> Dict[str, Any]:
        return {"loaded_model": self.current_model_name, "available_models": self.list_models()}

    def generate(self, prompt: str, config: Dict[str, Any], json_schema: Optional[Dict[str, Any]] = None) -> Union[str, Dict[str, Any]]:
        with self._lock:
            if not self.current_model:
                raise RuntimeError("No model loaded")

            grammar = None
            if json_schema:
                grammar = LlamaGrammar.from_json_schema(json.dumps(json_schema))

            # Qwen3 recommended defaults
            # Determine thinking mode: config takes precedence, then prompt tags
            thinking_config = config.get("thinking")
            if thinking_config is not None:
                is_thinking = thinking_config
            else:
                is_thinking = "/think" in prompt and "/no_think" not in prompt

            # Ensure the correct tag is present in the prompt
            if is_thinking:
                if "/think" not in prompt:
                    prompt = f"{prompt} /think"
                if "/no_think" in prompt:
                    prompt = prompt.replace("/no_think", "").strip()
            else:
                if "/no_think" not in prompt:
                    prompt = f"{prompt} /no_think"
                if "/think" in prompt:
                    prompt = prompt.replace("/think", "").strip()

            messages = [{"role": "user", "content": prompt}]
            # The llama_cpp types are not fully typed for our usage here; cast to Any for mypy.
            messages_any = cast(Any, messages)

            params: Dict[str, Any] = {
                "temperature": float(config.get("temperature", 0.6 if is_thinking else 0.7)),
                "top_p": float(config.get("top_p", 0.95 if is_thinking else 0.8)),
                "top_k": int(config.get("top_k", 20)),
                "min_p": float(config.get("min_p", 0.0)),
                "repeat_penalty": float(config.get("repeat_penalty", 1.1)),
                "presence_penalty": float(config.get("presence_penalty", 1.5)),
                "max_tokens": int(config.get("max_tokens", 32768)),
                "stop": cast(List[str], config.get("stop", ["<|endoftext|>", "<|im_end|>"])),
            }

            response = cast(Any, self.current_model.create_chat_completion(messages=messages_any, grammar=grammar, **params))

            # response may be a streaming iterator or a dict-like response; treat as Any and extract text
            output_text = str(response["choices"][0]["message"]["content"]) 

            # Clean up thinking tokens if thinking is disabled
            if not is_thinking:
                if "<think>" in output_text and "</think>" in output_text:
                    output_text = output_text.split("</think>")[-1].strip()
                elif "<think>" in output_text:
                    output_text = output_text.split("<think>")[-1].split("</think>")[-1].strip()

            if json_schema:
                try:
                    parsed = json.loads(output_text)
                    return cast(Dict[str, Any], parsed)
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON produced", "raw": output_text}

            return output_text
