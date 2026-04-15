"""
SOTA-2026: ТЗ Скоринг Платформа
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

load_dotenv()

from routers import upload, health

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


@app.get("/")
async def root():
    return {
        "service": "SOTA-2026 ТЗ Скоринг",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }
