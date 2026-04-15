"""История анализов ТЗ (сохранение в БД)."""
from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db import get_db
from db_models import AnalysisRecord, User
from deps import get_current_user
from report_builder import build_report_markdown

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analyses", tags=["analyses"])


class SaveAnalysisIn(BaseModel):
    filename: str = Field(..., max_length=512)
    result: dict = Field(..., description="JSON результата TZAuditResult")


class AnalysisListItem(BaseModel):
    id: int
    filename: str
    created_at: str
    total_score: int | None
    grade: str | None


@router.post("", status_code=201)
def save_analysis(
    body: SaveAnalysisIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        raw = json.dumps(body.result, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Некорректный JSON результата: {e}") from e
    rec = AnalysisRecord(user_id=user.id, filename=body.filename, result_json=raw)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return {"id": rec.id, "created_at": rec.created_at.isoformat()}


@router.get("", response_model=list[AnalysisListItem])
def list_analyses(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AnalysisListItem]:
    rows = (
        db.query(AnalysisRecord)
        .filter(AnalysisRecord.user_id == user.id)
        .order_by(AnalysisRecord.created_at.desc())
        .limit(100)
        .all()
    )
    out: list[AnalysisListItem] = []
    for r in rows:
        ts: int | None = None
        gr: str | None = None
        try:
            data = json.loads(r.result_json)
            ts = data.get("total_score")
            gr = data.get("grade")
        except json.JSONDecodeError:
            pass
        out.append(
            AnalysisListItem(
                id=r.id,
                filename=r.filename,
                created_at=r.created_at.isoformat(),
                total_score=ts,
                grade=gr,
            )
        )
    return out


@router.get("/{analysis_id}")
def get_analysis(
    analysis_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    rec = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if rec is None or rec.user_id != user.id:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    try:
        data = json.loads(rec.result_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Повреждённые данные")
    return {
        "id": rec.id,
        "filename": rec.filename,
        "created_at": rec.created_at.isoformat(),
        "result": data,
    }


@router.delete("/{analysis_id}", status_code=204)
def delete_analysis(
    analysis_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    rec = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if rec is None or rec.user_id != user.id:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    db.delete(rec)
    db.commit()
    return Response(status_code=204)


@router.get("/{analysis_id}/report")
def download_report(
    analysis_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    rec = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if rec is None or rec.user_id != user.id:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    try:
        data = json.loads(rec.result_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Повреждённые данные")
    md = build_report_markdown(rec.filename, data)
    filename_safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in rec.filename)[:80]
    return Response(
        content=md.encode("utf-8"),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="report_{filename_safe}.md"'},
    )
