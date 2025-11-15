import os
import json
import yaml
import requests
from pathlib import Path
from google import genai
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
MODELS_JSON = ROOT / "config" / "models.json"
PROFILE_YAML = ROOT / "config" / "profiles.yaml"

class ModelManager:
    def __init__(self):
        self.config = json.loads(MODELS_JSON.read_text())
        self.profile = yaml.safe_load(PROFILE_YAML.read_text())

        self.text_model_key = self.profile["llm"]["text_generation"]
        self.model_info = self.config["models"][self.text_model_key]
        self.model_type = self.model_info["type"]

        # ✅ Gemini initialization (your style)
        if self.model_type == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            self.client = genai.Client(api_key=api_key)

    async def generate_text(self, prompt: str) -> str:
        if self.model_type == "gemini":
            return self._gemini_generate(prompt)

        elif self.model_type == "ollama":
            return self._ollama_generate(prompt)

        raise NotImplementedError(f"Unsupported model type: {self.model_type}")

    def _gemini_generate(self, prompt: str) -> str:
        import time
        max_retries = 3
        base_delay = 2  # Start with 2 seconds
        
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_info["model"],
                    contents=prompt
                )

                # ✅ Safely extract response text
                try:
                    return response.text.strip()
                except AttributeError:
                    try:
                        return response.candidates[0].content.parts[0].text.strip()
                    except Exception:
                        return str(response)
            except Exception as e:
                error_str = str(e)
                # Check if it's a rate limit error (429)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        # Extract retry delay from error if available, otherwise use exponential backoff
                        delay = base_delay * (2 ** attempt)  # 2s, 4s, 8s
                        # Try to extract suggested delay from error message
                        if "retry in" in error_str.lower() or "retryDelay" in error_str:
                            # Parse delay from error (e.g., "retry in 1.8s" or retryDelay: '59s')
                            import re
                            delay_match = re.search(r'retry.*?(\d+(?:\.\d+)?)\s*s', error_str, re.IGNORECASE)
                            if delay_match:
                                delay = float(delay_match.group(1)) + 1  # Add 1 second buffer
                        
                        print(f"[model_manager] Rate limit hit (429), waiting {delay:.1f}s before retry {attempt+1}/{max_retries}...")
                        time.sleep(delay)
                        continue
                    else:
                        raise Exception(f"Rate limit exceeded after {max_retries} retries. Please wait a minute and try again.")
                else:
                    # Not a rate limit error, re-raise immediately
                    raise

    def _ollama_generate(self, prompt: str) -> str:
        response = requests.post(
            self.model_info["url"]["generate"],
            json={"model": self.model_info["model"], "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        return response.json()["response"].strip()
