"""
Groq AI Client implementation.
Provides free, high-speed cloud inference for open-source Llama models (e.g. llama-3.1-8b-instant)
using Groq's 100% free tier. Requires no credit card.
Used for public cloud deployments (Streamlit Community Cloud).
"""
import json
import logging
from typing import List, Tuple, Optional
import requests

from .base import BaseAIProvider

logger = logging.getLogger(__name__)

DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"


class GroqClient(BaseAIProvider):
    """Client for free Groq Cloud LLM execution."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 60,
    ):
        self.api_key = (api_key or "").strip()
        self.model = model or DEFAULT_GROQ_MODEL
        self.timeout = timeout
        self.base_url = "https://api.groq.com/openai/v1"

    def is_available(self) -> Tuple[bool, str]:
        """Verify if the Groq API key is valid and service is reachable."""
        if not self.api_key:
            return False, "Groq API key not provided."
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            res = requests.get(f"{self.base_url}/models", headers=headers, timeout=5)
            if res.status_code == 200:
                return True, f"Groq Cloud Online ({self.model})"
            return False, f"Groq returned status {res.status_code}: {res.text}"
        except Exception as e:
            return False, f"Could not connect to Groq: {str(e)}"

    def list_models(self) -> List[str]:
        """List common free Llama models available on Groq."""
        return [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "llama3-8b-8192",
        ]

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
    ) -> str:
        """Generate text via Groq OpenAI-compatible REST API."""
        if not self.api_key:
            raise RuntimeError(
                "Groq API key is missing. Add your free Groq API key in Streamlit Secrets or sidebar."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            else:
                raise RuntimeError(
                    f"Groq API error (status {response.status_code}): {response.text}"
                )
        except requests.exceptions.Timeout:
            raise TimeoutError("Groq request timed out.")
        except Exception as e:
            if isinstance(e, (RuntimeError, TimeoutError)):
                raise e
            raise RuntimeError(f"Unexpected error communicating with Groq: {str(e)}")
