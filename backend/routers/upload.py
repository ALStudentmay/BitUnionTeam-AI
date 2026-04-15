"""
Upload & Score Router
POST /api/upload  — загрузка и парсинг файла в Markdown
POST /api/score   — скоринг Markdown-текста через LLM
"""
from __future__ import annotations

import io
import logging
import os
import httpx

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services.document_parser import parse_to_markdown
from services.ai_scorer import TZAuditResult, score_tz

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".docx", ".pdf", ".txt", ".md"}
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "50")) * 1024 * 1024  # bytes


class ParseResponse(BaseModel):
    filename: str
    markdown: str
    char_count: int
    word_count: int


class ScoreRequest(BaseModel):
    markdown: str
    filename: str = "document.docx"


# ──────────────────────────────────────────────────────────────────
#  POST /api/upload — Парсинг файла → Markdown
# ──────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=ParseResponse)
async def upload_and_parse(file: UploadFile = File(...)):
    """
    Принимает DOCX или PDF файл.
    Возвращает чистый Markdown-текст для последующего скоринга.
    """
    # Валидация имени файла
    filename = file.filename or "unknown"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Неподдерживаемый формат файла '{ext}'. "
                   f"Допустимые: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Читаем файл
    file_bytes = await file.read()

    # Проверяем размер
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Файл слишком большой. Максимум: {os.getenv('MAX_FILE_SIZE_MB', '50')} МБ",
        )

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Файл пустой")

    logger.info(f"Получен файл: {filename} ({len(file_bytes) / 1024:.1f} КБ)")

    try:
        markdown = parse_to_markdown(file_bytes, filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка парсинга: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга файла: {str(e)}")

    if not markdown.strip():
        raise HTTPException(
            status_code=422,
            detail="Файл не содержит извлекаемого текста. Проверьте формат.",
        )

    word_count = len(markdown.split())
    logger.info(f"Парсинг успешен: {len(markdown)} символов, {word_count} слов")

    return ParseResponse(
        filename=filename,
        markdown=markdown,
        char_count=len(markdown),
        word_count=word_count,
    )


# ──────────────────────────────────────────────────────────────────
#  POST /api/score — LLM-скоринг Markdown текста
# ──────────────────────────────────────────────────────────────────

@router.post("/score", response_model=TZAuditResult)
async def score_document(request: ScoreRequest):
    """
    Принимает Markdown-текст ТЗ.
    Возвращает полный аудит: баллы по 7 критериям, ошибки, улучшения.
    """
    if not request.markdown.strip():
        raise HTTPException(status_code=400, detail="Текст ТЗ не может быть пустым")

    if len(request.markdown) < 100:
        raise HTTPException(
            status_code=400,
            detail="Текст ТЗ слишком короткий (менее 100 символов). Загрузите полный документ.",
        )

    logger.info(f"Запуск LLM-скоринга для: {request.filename}")

    try:
        result = await score_tz(request.markdown)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Ошибка разбора ответа LLM: {str(e)}")
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Не удалось подключиться к LLM. Проверьте, запущен ли Ollama или указан ли API ключ.",
        )
    except Exception as e:
        logger.error(f"Ошибка скоринга: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка скоринга: {str(e)}")

    return result


# ──────────────────────────────────────────────────────────────────
#  POST /api/analyze — Комбо: загрузка + скоринг за один запрос
# ──────────────────────────────────────────────────────────────────

@router.post("/analyze", response_model=TZAuditResult)
async def analyze_file(file: UploadFile = File(...)):
    """
    Удобный endpoint: загружает файл, парсит и сразу скорит.
    Используется фронтом для одношагового анализа.
    """
    # Шаг 1: Парсинг
    parse_result = await upload_and_parse(file)

    # Шаг 2: Скоринг
    score_req = ScoreRequest(
        markdown=parse_result.markdown,
        filename=parse_result.filename,
    )
    return await score_document(score_req)
