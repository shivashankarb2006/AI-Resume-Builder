"""
Abstract Base AI Provider for AI Resume Builder.
Allows switching or extending AI providers (Ollama, local vLLM, etc.)
without altering application business logic.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional


class BaseAIProvider(ABC):
    """Abstract interface for local and modular AI providers."""

    @abstractmethod
    def is_available(self) -> Tuple[bool, str]:
        """
        Check if the AI provider engine is reachable and running.
        Returns: (is_available, status_message)
        """
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """
        Return list of locally installed model names.
        """
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
    ) -> str:
        """
        Generate text or JSON response from the language model.
        """
        pass
