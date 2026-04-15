"""
Чат-ассистент и генерация примера ТЗ (тот же LLM_PROVIDER, что и скоринг).
"""
from __future__ import annotations

import logging
import os

import httpx

logger = logging.getLogger(__name__)

CHAT_SYSTEM = """Ты опытный консультант по подготовке технических заданий (ТЗ) на научно-исследовательские работы
в рамках грантового финансирования (НИР, ПЦФ). Отвечай кратко и по делу на русском языке.
Если дан фрагмент ТЗ, учитывай его при ответе. Не выдумывай факты о документе — опирайся только на переданный контекст."""


async def assistant_chat_reply(user_message: str, tz_context: str | None) -> str:
    ctx = (tz_context or "").strip()[:12000]
    block = f"Фрагмент ТЗ для контекста:\n{ctx}\n\n" if ctx else ""
    full = f"{block}Вопрос: {user_message.strip()}"
    return await _route_llm_text(CHAT_SYSTEM, full)


async def generate_example_tz(topic: str | None) -> str:
    t = (topic or "инновационные цифровые технологии в энергетике").strip()
    prompt = f"""Сгенерируй краткий **пример структуры** технического задания НИР по теме: «{t}».
Обязательно включи заголовки разделов в духе официального шаблона:
1) Общие сведения (приоритет, направление)
2) Цели и задачи
3) Стратегические документы (с конкретными пунктами программ)
4) Ожидаемые результаты с KPI (числа)
5) Бюджет по годам (тыс. тенге)
Используй Markdown (# ##). Объём — 1–2 экрана, без воды."""
    return await _route_llm_text(
        "Ты помогаешь составлять ТЗ для грантов. Пиши только на русском.",
        prompt,
    )


async def _route_llm_text(system_prompt: str, user_prompt: str) -> str:
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    if provider == "groq":
        return await _groq_text(system_prompt, user_prompt)
    if provider == "openai":
        return await _openai_text(system_prompt, user_prompt)
    if provider == "anthropic":
        return await _anthropic_text(system_prompt, user_prompt)
    if provider == "gemini":
        return await _gemini_text(system_prompt, user_prompt)
    return await _ollama_text(system_prompt, user_prompt)


async def _groq_text(system_prompt: str, user_prompt: str) -> str:
    from openai import AsyncOpenAI

    api_key = (os.getenv("GROQ_API_KEY") or "").strip()
    if not api_key:
        raise ValueError("GROQ_API_KEY не задан")
    model = (os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile").strip()
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )
    r = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=4096,
    )
    return (r.choices[0].message.content or "").strip()


async def _gemini_text(system_prompt: str, user_prompt: str) -> str:
    import google.generativeai as genai

    api_key = (os.getenv("GOOGLE_API_KEY") or "").strip()
    if not api_key:
        raise ValueError("GOOGLE_API_KEY не задан")
    genai.configure(api_key=api_key)
    model_name = (os.getenv("GOOGLE_MODEL") or "gemini-2.0-flash").strip()
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt,
        generation_config={"temperature": 0.4, "max_output_tokens": 4096},
    )
    r = await model.generate_content_async(user_prompt)
    return (r.text or "").strip()


async def _ollama_text(system_prompt: str, user_prompt: str) -> str:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:14b")
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{base_url}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
            },
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"].strip()


async def _openai_text(system_prompt: str, user_prompt: str) -> str:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    r = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=4096,
    )
    return (r.choices[0].message.content or "").strip()


async def _anthropic_text(system_prompt: str, user_prompt: str) -> str:
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    msg = await client.messages.create(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
        temperature=0.4,
    )
    return msg.content[0].text.strip()
