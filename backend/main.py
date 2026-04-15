"""
SOTA-2026: ТЗ Скоринг Платформа
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# Явно грузим backend/.env — иначе при запуске uvicorn из другой cwd ключ не подхватывается
_backend_root = Path(__file__).resolve().parent
load_dotenv(_backend_root / ".env")
load_dotenv(_backend_root.parent / ".env")  # опционально: .env в корне репозитория

from db import init_db
from routers import analyses, auth_api, chat_api, extra_api, health, report_api, upload

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 SOTA-2026 ТЗ Скоринг Платформа стартует...")
    logger.info(f"   LLM Provider: {os.getenv('LLM_PROVIDER', 'ollama')}")
    init_db()
    logger.info("   БД SQLite инициализирована.")
    yield
    logger.info("Сервер остановлен.")


app = FastAPI(
    title="SOTA-2026 ТЗ Скоринг API",
    description="Платформа умного скоринга и улучшения научных Технических Заданий",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(upload.router, prefix="/api", tags=["scoring"])
app.include_router(auth_api.router, prefix="/api/auth", tags=["auth"])
app.include_router(analyses.router, prefix="/api", tags=["analyses"])
app.include_router(chat_api.router, prefix="/api", tags=["chat"])
app.include_router(extra_api.router, prefix="/api", tags=["extra"])
app.include_router(report_api.router, prefix="/api", tags=["report"])


@app.get("/")
async def root():
    return {
        "service": "SOTA-2026 ТЗ Скоринг",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }
