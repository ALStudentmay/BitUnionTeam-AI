"""Текстовый итоговый отчёт (Markdown) по результату аудита ТЗ."""
from __future__ import annotations

import json
from typing import Any


def build_report_markdown(filename: str, result: dict[str, Any]) -> str:
    """Формирует полный отчёт для скачивания (п. ТЗ: итоговый отчёт)."""
    lines: list[str] = [
        f"# Итоговый отчёт по анализу ТЗ",
        "",
        f"- **Файл:** {filename}",
        f"- **Итоговый балл:** {result.get('total_score', '—')}/100",
        f"- **Оценка:** {result.get('grade', '—')}",
        "",
        "## Рекомендуемая структура проверки (кратко)",
        "",
        "Отчёт включает: сводную оценку, разбор по критериям, критические замечания, сильные стороны и фрагмент улучшенного ТЗ.",
        "",
        "## Баллы по критериям",
        "",
    ]
    for c in result.get("criteria") or []:
        name = c.get("name", "")
        score = c.get("score", "")
        mx = c.get("max_score", "")
        lines.append(f"### {name}")
        lines.append(f"**{score} / {mx}**")
        lines.append("")
        lines.append(c.get("reasoning", "") or "")
        lines.append("")

    lines.extend(
        [
            "## Критические ошибки и пробелы",
            "",
        ]
    )
    for i, err in enumerate(result.get("critical_errors") or [], 1):
        lines.append(f"{i}. {err}")
    lines.extend(["", "## Сильные стороны", ""])
    for s in result.get("strengths") or []:
        lines.append(f"- {s}")

    lines.extend(
        [
            "",
            "## Улучшенный фрагмент ТЗ (предложение ИИ)",
            "",
            result.get("improved_markdown", "") or "_нет данных_",
            "",
            "---",
            "",
            "*Сформировано автоматически системой аудита ТЗ.*",
        ]
    )
    return "\n".join(lines)
