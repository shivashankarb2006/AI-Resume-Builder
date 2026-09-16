"""
Ollama AI Client implementation.
Communicates directly with the local Ollama instance via HTTP REST API.
Operates 100% locally with zero cloud API keys.
"""
import json
import logging
from typing import List, Tuple, Optional
import requests

from .base import BaseAIProvider
import config

logger = logging.getLogger(__name__)


class OllamaClient(BaseAIProvider):
    """Client for local Ollama LLM execution."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.base_url = (base_url or config.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or config.OLLAMA_MODEL
        self.timeout = timeout or config.OLLAMA_TIMEOUT_SECONDS

    def is_available(self) -> Tuple[bool, str]:
        """
        Verify if the Ollama service is reachable.
        Returns (is_online, message).
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=3,
            )
            if response.status_code == 200:
                return True, f"Ollama is online ({self.base_url})"
            return False, f"Ollama returned HTTP status {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, (
                "Ollama is not running. Please start Ollama (e.g. run 'ollama serve' "
                "or start Ollama Desktop) and try again."
            )
        except requests.exceptions.Timeout:
            return False, "Connection to Ollama timed out. Ensure the Ollama service is responsive."
        except Exception as e:
            return False, f"Could not connect to Ollama: {str(e)}"

    def list_models(self) -> List[str]:
        """Fetch all installed model tags from the local Ollama instance."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                # Return list of model names (e.g. "llama3.2:latest", "llama3.2")
                names = []
                for m in models:
                    name = m.get("name")
                    if name:
                        names.append(name)
                return names
        except Exception as e:
            logger.warning(f"Error fetching Ollama models: {e}")
        return []

    def is_model_installed(self, model_name: Optional[str] = None) -> bool:
        """Check whether the configured or specified model is installed."""
        target = model_name or self.model
        installed = self.list_models()
        # Check direct match or match without tag e.g. "llama3.2" matches "llama3.2:latest"
        for m in installed:
            if m == target or m.split(":")[0] == target:
                return True
        return False

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
    ) -> str:
        """
        Send generation request to Ollama `/api/generate`.
        Handles errors and provides human-friendly guidance if model is missing.
        """
        # Validate model presence
        if not self.is_model_installed():
            raise RuntimeError(
                f"Model '{self.model}' is not installed in Ollama.\n"
                f"Please run in your terminal: ollama pull {self.model}"
            )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for grounded factual generation
                "top_p": 0.9,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt
        if json_mode:
            payload["format"] = "json"

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            elif response.status_code == 404:
                raise RuntimeError(
                    f"Model '{self.model}' was not found by Ollama. Run: ollama pull {self.model}"
                )
            else:
                raise RuntimeError(
                    f"Ollama generation failed with status {response.status_code}: {response.text}"
                )
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "Could not connect to Ollama. Ensure Ollama is running at " + self.base_url
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Ollama request timed out after {self.timeout} seconds. Try using a lighter model like llama3.2:1b."
            )
        except Exception as e:
            if isinstance(e, (RuntimeError, ConnectionError, TimeoutError)):
                raise e
            raise RuntimeError(f"Unexpected error communicating with Ollama: {str(e)}")
