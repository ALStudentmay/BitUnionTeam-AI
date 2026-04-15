"""Чат с AI-ассистентом по ТЗ."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.assistant_llm import assistant_chat_reply

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


class ChatIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    tz_context: str | None = Field(None, max_length=50000)


class ChatOut(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatOut)
async def chat_endpoint(body: ChatIn) -> ChatOut:
    try:
        reply = await assistant_chat_reply(body.message, body.tz_context)
    except Exception as e:
        logger.exception("chat error")
        raise HTTPException(status_code=500, detail=str(e)) from e
    return ChatOut(reply=reply)
