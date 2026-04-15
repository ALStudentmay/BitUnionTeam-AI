import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Добавляем backend в sys.path, чтобы использовать наш парсер
BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(BASE_DIR / "backend"))

from services.document_parser import parse_to_markdown

# Загружаем ключи из конфигурации бэкенда
load_dotenv(BASE_DIR / "backend" / ".env")

# Настраиваем Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",  # Быстрая и дешевая модель для генерации "мусора"
    generation_config={"temperature": 0.8}
)

# Профили "плохих" ТЗ
PROFILES = {
    "bad_tz_no_kpi": (
        "Без цифр",
        "Твоя задача — переписать ТЗ так, чтобы оно выглядело крайне расплывчатым. "
        "Удали абсолютно ВСЕ числа, метрики, суммы и количественные KPI (RMSE, Q1, 40%, и т.д.). "
        "Вместо них используй абстрактные фразы: 'улучшить', 'сделать хорошо', 'добиться значительных результатов', "
        "'опубликовать статьи' (без указания где и сколько)."
    ),
    "bad_tz_budget_chaos": (
        "Хаос в бюджете",
        "Твоя задача — сломать логику бюджета и плана-графика. "
        "Сделай так, чтобы суммы по годам абсолютно не сходились с итоговой суммой (например, за год 1 — 10 млн, за год 2 — 15 млн, "
        "а итого 100 млн). Добавь нелогичные закупки вроде 'кофемашина за 5 миллионов' и сделай сроки реализации физически невозможными."
    ),
    "bad_tz_no_innovation": (
        "Без научной новизны",
        "Твоя задача — полностью удалить любую научную и исследовательскую составляющую. "
        "Перепиши ТЗ так, словно это обычный тендер на закупку готового софта или оборудования. "
        "Удали раздел 'Научная новизна' или напиши там откровенную чушь. Замени разработку алгоритмов на 'покупку готовых лицензий'."
    ),
    "bad_tz_structural_hell": (
        "Структурный ад",
        "Твоя задача — разрушить структуру ТЗ. Перепутай все разделы местами (например, 'Бюджет' в самом начале, а 'Цели' в конце). "
        "Удали половину обязательных разделов (например, 'Актуальность' и 'Ожидаемые результаты'). "
        "Добавь кучу воды и канцелярита, чтобы текст читался максимально тяжело и нелогично."
    )
}

async def generate_bad_tz(reference_text: str, filename: str, profile_desc: str, instruction: str):
    print(f"🔄 Генерируем [{filename}] (Профиль: {profile_desc})...")
    
    prompt = f"""
У меня есть эталонное Техническое Задание на научный проект.
{instruction}

ЭТАЛОННОЕ ТЗ:
=======================
{reference_text}
=======================

Выведи ТОЛЬКО переписанный текст ТЗ в формате Markdown без лишних комментариев.
"""
    
    try:
        response = await model.generate_content_async(prompt)
        
        output_dir = BASE_DIR / "test_data"
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / f"{filename}.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response.text)
            
        print(f"✅ Успешно сохранено: {output_path}")
        
    except Exception as e:
        print(f"❌ Ошибка при генерации {filename}: {e}")

async def main():
    print("🚀 Старт генератора 'плохих' ТЗ для демо-питча\n")
    
    source_file = BASE_DIR / "ТЗ Цифровой полигон.docx"
    if not source_file.exists():
        print(f"❌ Сурсовой файл не найден: {source_file}")
        return

    print("📄 Читаем эталонное ТЗ...")
    try:
        with open(source_file, "rb") as f:
            file_bytes = f.read()
        reference_markdown = parse_to_markdown(file_bytes, source_file.name)
    except Exception as e:
        print(f"❌ Ошибка парсинга эталонного ТЗ: {e}")
        return

    print(f"✅ ТЗ успешно прочитано ({len(reference_markdown)} символов). Запускаем Gemini 1.5 Flash...\n")
    
    tasks = []
    for file_key, (desc, instr) in PROFILES.items():
        tasks.append(generate_bad_tz(reference_markdown, file_key, desc, instr))
    
    await asyncio.gather(*tasks)
    
    print("\n🎉 Все тестовые ТЗ успешно сгенерированы! Проект готов к демо (Code Freeze).")

if __name__ == "__main__":
    asyncio.run(main())
