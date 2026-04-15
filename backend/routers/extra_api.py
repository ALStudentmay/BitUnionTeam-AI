"""Доп. endpoints: пример ТЗ."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.assistant_llm import generate_example_tz

logger = logging.getLogger(__name__)
router = APIRouter(tags=["extra"])


class ExampleIn(BaseModel):
    topic: str | None = Field(None, max_length=500)


class ExampleOut(BaseModel):
    markdown: str


@router.post("/example-tz", response_model=ExampleOut)
async def example_tz_endpoint(body: ExampleIn) -> ExampleOut:
    try:
        md = await generate_example_tz(body.topic)
    except Exception as e:
        logger.exception("example-tz")
        raise HTTPException(status_code=500, detail=str(e)) from e
    return ExampleOut(markdown=md)
