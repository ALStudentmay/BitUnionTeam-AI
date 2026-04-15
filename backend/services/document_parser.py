"""
Document Parser Service
=======================
Конвертирует загруженные файлы (DOCX, PDF) в чистый Markdown.

Стратегия (в порядке приоритета):
  1. python-docx  → для .docx файлов (самый точный, полностью офлайн)
  2. PyMuPDF (fitz) → для .pdf файлов (быстрый, без Tesseract)
  3. unstructured  → универсальный fallback
"""
from __future__ import annotations

import io
import logging
import os
import re
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────
#  Public API
# ──────────────────────────────────────────────────────────────────

def parse_to_markdown(file_bytes: bytes, filename: str) -> str:
    """
    Принимает сырые байты файла и его имя.
    Возвращает строку в формате Markdown.
    
    Структура вывода:
      1. Автоматический отчёт о наличии обязательных разделов по шаблону ТЗ
      2. Полный текст документа в Markdown
    """
    ext = Path(filename).suffix.lower()
    logger.info(f"Парсинг файла: {filename} (расширение: {ext})")

    try:
        if ext == ".docx":
            raw_md = _parse_docx(file_bytes)
        elif ext == ".pdf":
            raw_md = _parse_pdf(file_bytes)
        elif ext in (".txt", ".md"):
            raw_md = file_bytes.decode("utf-8", errors="replace")
        else:
            # Попробуем через unstructured как финальный fallback
            raw_md = _parse_unstructured(file_bytes, filename)

        # Добавляем структурный анализ по официальному шаблону ТЗ
        structural_report = check_tz_structure(raw_md)
        return structural_report + raw_md

    except Exception as e:
        logger.error(f"Ошибка парсинга {filename}: {e}", exc_info=True)
        raise ValueError(f"Не удалось разобрать файл '{filename}': {e}") from e


# ──────────────────────────────────────────────────────────────────
#  DOCX Parser (python-docx)
# ──────────────────────────────────────────────────────────────────

def _parse_docx(file_bytes: bytes) -> str:
    """Конвертирует DOCX → Markdown, сохраняя структуру заголовков и таблиц."""
    from docx import Document
    from docx.oxml.ns import qn

    doc = Document(io.BytesIO(file_bytes))
    md_lines: list[str] = []

    for block in _iter_block_items(doc):
        if block["type"] == "paragraph":
            para = block["element"]
            style_name = para.style.name if para.style else ""
            text = para.text.strip()

            if not text:
                md_lines.append("")
                continue

            # Заголовки
            if style_name.startswith("Heading"):
                try:
                    level = int(style_name.split()[-1])
                except ValueError:
                    level = 2
                level = min(level, 6)
                md_lines.append(f"{'#' * level} {text}")
            # Нумерованные и маркированные списки
            elif style_name in ("List Paragraph", "List Bullet", "List Number",
                                 "Список", "Списковый абзац"):
                md_lines.append(f"- {text}")
            else:
                md_lines.append(text)

        elif block["type"] == "table":
            md_lines.append("")
            md_lines.extend(_table_to_markdown(block["element"]))
            md_lines.append("")

    raw_md = "\n".join(md_lines)
    return _clean_markdown(raw_md)


def _iter_block_items(doc):
    """Итерирует параграфы и таблицы в правильном порядке из тела документа."""
    from docx.oxml.ns import qn

    body = doc.element.body
    for child in body:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag == "p":
            from docx.text.paragraph import Paragraph
            yield {"type": "paragraph", "element": Paragraph(child, doc)}
        elif tag == "tbl":
            from docx.table import Table
            yield {"type": "table", "element": Table(child, doc)}


def _table_to_markdown(table) -> list[str]:
    """Конвертирует таблицу docx в Markdown-таблицу."""
    rows_md: list[str] = []
    for i, row in enumerate(table.rows):
        cells = [cell.text.replace("\n", " ").strip() for cell in row.cells]
        # Убираем дублированные ячейки (merge artifacts)
        cleaned: list[str] = []
        prev = None
        for c in cells:
            if c != prev:
                cleaned.append(c)
                prev = c
            else:
                cleaned.append("")

        row_str = "| " + " | ".join(cleaned) + " |"
        rows_md.append(row_str)

        # После первой строки — разделитель
        if i == 0:
            sep = "| " + " | ".join(["---"] * len(cleaned)) + " |"
            rows_md.append(sep)

    return rows_md


# ──────────────────────────────────────────────────────────────────
#  PDF Parser (PyMuPDF)
# ──────────────────────────────────────────────────────────────────

def _parse_pdf(file_bytes: bytes) -> str:
    """Конвертирует PDF → Markdown через PyMuPDF (без OCR)."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        md_lines: list[str] = []

        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block.get("type") != 0:  # 0 = text block
                    continue
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    if not spans:
                        continue

                    # Определяем размер шрифта для заголовков
                    avg_size = sum(s["size"] for s in spans) / len(spans)
                    text = " ".join(s["text"] for s in spans).strip()

                    if not text:
                        continue

                    if avg_size >= 18:
                        md_lines.append(f"# {text}")
                    elif avg_size >= 14:
                        md_lines.append(f"## {text}")
                    elif avg_size >= 12:
                        md_lines.append(f"### {text}")
                    else:
                        md_lines.append(text)

            md_lines.append("\n---\n")  # разделитель страниц

        doc.close()
        return _clean_markdown("\n".join(md_lines))

    except ImportError:
        logger.warning("PyMuPDF не установлен, пробуем unstructured...")
        return _parse_unstructured(file_bytes, "file.pdf")


# ──────────────────────────────────────────────────────────────────
#  Unstructured Fallback
# ──────────────────────────────────────────────────────────────────

def _parse_unstructured(file_bytes: bytes, filename: str) -> str:
    """Fallback через библиотеку unstructured."""
    try:
        from unstructured.partition.auto import partition

        suffix = Path(filename).suffix or ".bin"
        fd, tmp_name = tempfile.mkstemp(suffix=suffix)
        tmp_path = Path(tmp_name)
        try:
            os.write(fd, file_bytes)
        finally:
            os.close(fd)

        try:
            elements = partition(filename=str(tmp_path))
        finally:
            tmp_path.unlink(missing_ok=True)

        md_lines: list[str] = []
        for el in elements:
            category = getattr(el, "category", "NarrativeText")
            text = str(el).strip()
            if not text:
                continue
            if category == "Title":
                md_lines.append(f"## {text}")
            elif category in ("ListItem",):
                md_lines.append(f"- {text}")
            else:
                md_lines.append(text)

        return _clean_markdown("\n".join(md_lines))
    except Exception as e:
        logger.error(f"unstructured fallback тоже не сработал: {e}")
        raise


# ──────────────────────────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────────────────────────

def _clean_markdown(text: str) -> str:
    """Убирает лишние пустые строки и пробелы."""
    # Максимум 2 пустые строки подряд
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Убираем пробелы в конце строк
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip()


# ──────────────────────────────────────────────────────────────────
#  Анализ структуры ТЗ по официальному шаблону
# ──────────────────────────────────────────────────────────────────

# Ключевые фразы для обнаружения разделов официального шаблона ТЗ
# (из "Шаблон для ТЗ рус.docx")
_OFFICIAL_SECTIONS: list[tuple[str, list[str]]] = [
    (
        "Раздел 1 — Общие сведения (приоритет, направление)",
        [
            "общие сведения", "наименование приоритета", "специализированного направления",
            "1.1", "1.2",
        ],
    ),
    (
        "Раздел 2 — Цели и задачи программы",
        [
            "цели и задачи", "цель программы", "цель проекта",
            "для достижения поставленной цели", "2.1", "2.2",
        ],
    ),
    (
        "Раздел 3 — Стратегические и программные документы",
        [
            "стратегических и программных документов", "стратегических документов",
            "какие пункты", "концепция развития", "гпиир", "стратегия 2050",
            "стратегия 2030", "национальный план", "sdg", "сдг", "постановление",
        ],
    ),
    (
        "Раздел 4 — Ожидаемые результаты (с KPI)",
        [
            "ожидаемые результаты", "прямые результаты", "конечный результат",
            "scopus", "web of science", "wos", "патент", "публикаци",
            "4.1", "4.2",
        ],
    ),
    (
        "Раздел 5 — Бюджет (предельная сумма по годам)",
        [
            "предельная сумма", "бюджет", "тыс. тенге", "тысяч тенге",
            "финансирование", "по годам",
        ],
    ),
]


def check_tz_structure(markdown_text: str) -> str:
    """
    Проверяет наличие обязательных разделов ТЗ по официальному шаблону.
    Возвращает строку-отчёт, которая будет добавлена в начало Markdown.
    """
    text_lower = markdown_text.lower()
    report_lines = [
        "## [СТРУКТУРНЫЙ АНАЛИЗ ТЗ — АВТОМАТИЧЕСКИЙ ОТЧЁТ]",
        "",
        "Проверка наличия обязательных разделов по официальному шаблону ТЗ (НИР ПЦФ):",
        "",
    ]

    found_sections: list[str] = []
    missing_sections: list[str] = []

    for section_name, keywords in _OFFICIAL_SECTIONS:
        found = any(kw in text_lower for kw in keywords)
        status = "✅ НАЙДЕН" if found else "❌ ОТСУТСТВУЕТ"
        report_lines.append(f"- {status}: {section_name}")
        if found:
            found_sections.append(section_name)
        else:
            missing_sections.append(section_name)

    report_lines.append("")
    if missing_sections:
        report_lines.append(
            f"**ВНИМАНИЕ: Отсутствует {len(missing_sections)} из {len(_OFFICIAL_SECTIONS)} "
            f"обязательных разделов:**"
        )
        for sec in missing_sections:
            report_lines.append(f"  - {sec}")
    else:
        report_lines.append("**Все 5 обязательных разделов присутствуют.**")

    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    return "\n".join(report_lines)
