"""Health check router"""
from fastapi import APIRouter
import os

router = APIRouter()


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "llm_provider": os.getenv("LLM_PROVIDER", "ollama"),
        "model": _get_active_model(),
    }


def _get_active_model() -> str:
    provider = os.getenv("LLM_PROVIDER", "groq")
    if provider == "groq":
        return os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    elif provider == "openai":
        return os.getenv("OPENAI_MODEL", "gpt-4o")
    elif provider == "anthropic":
        return os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    elif provider == "gemini":
        return os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
    else:
        return os.getenv("OLLAMA_MODEL", "qwen2.5:14b")
