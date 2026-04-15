"""Сборка итогового отчёта без сохранения в БД (для скачивания с дашборда)."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from report_builder import build_report_markdown

router = APIRouter(prefix="/report", tags=["report"])


class ReportBuildIn(BaseModel):
    filename: str
    result: dict


class ReportBuildOut(BaseModel):
    markdown: str


@router.post("/build", response_model=ReportBuildOut)
def report_build(body: ReportBuildIn) -> ReportBuildOut:
    md = build_report_markdown(body.filename, body.result)
    return ReportBuildOut(markdown=md)
