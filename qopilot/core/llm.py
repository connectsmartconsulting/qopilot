"""Provider abstraction: Anthropic, OpenAI-compatible, or Offline."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

import httpx


@dataclass
class LLMResponse:
    text: str
    model: str
    provider: str
    offline: bool = False


class Provider(ABC):
    name: str = "abstract"

    @abstractmethod
    def complete(self, system: str, user: str, max_tokens: int = 1500) -> LLMResponse:
        ...


class AnthropicProvider(Provider):
    name = "anthropic"

    def __init__(self, api_key: str | None = None, model: str = "claude-3-5-sonnet-latest"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model

    def complete(self, system: str, user: str, max_tokens: int = 1500) -> LLMResponse:
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        r = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": max_tokens,
                "system": system,
                "messages": [{"role": "user", "content": user}],
                "temperature": 0.0,
            },
            timeout=60.0,
        )
        r.raise_for_status()
        data = r.json()
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        return LLMResponse(text=text, model=self.model, provider=self.name)


class OpenAICompatibleProvider(Provider):
    name = "openai"

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        url: str = "https://api.openai.com/v1/chat/completions",
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.url = url

    def complete(self, system: str, user: str, max_tokens: int = 1500) -> LLMResponse:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        r = httpx.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "max_tokens": max_tokens,
                "temperature": 0.0,
            },
            timeout=60.0,
        )
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"]
        return LLMResponse(text=text, model=self.model, provider=self.name)


class OfflineProvider(Provider):
    """Deterministic template-based generator for CI, demos, and air-gapped use.

    Produces less polished output than a real LLM, but sufficient for engineering
    review and first drafts. The offline provider is intentionally simple and
    never calls any external service.
    """

    name = "offline"

    def __init__(self):
        self.model = "offline-template"

    def complete(self, system: str, user: str, max_tokens: int = 1500) -> LLMResponse:
        # The caller (author / interpret) handles offline rendering directly.
        # If the abstract interface is used, return a clear marker.
        return LLMResponse(
            text="[offline provider: caller should route to its own renderer]",
            model=self.model,
            provider=self.name,
            offline=True,
        )


def autodetect_provider(offline: bool = False) -> Provider:
    """Pick a provider: explicit offline > Anthropic > OpenAI > offline fallback."""
    if offline:
        return OfflineProvider()
    if os.getenv("ANTHROPIC_API_KEY"):
        return AnthropicProvider()
    if os.getenv("OPENAI_API_KEY"):
        return OpenAICompatibleProvider()
    return OfflineProvider()
