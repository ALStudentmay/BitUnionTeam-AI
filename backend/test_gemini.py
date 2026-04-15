import asyncio
import os
import sys
from pathlib import Path

# Добавляем родительскую папку в sys.path, чтобы работал импорт из проекта
sys.path.append(str(Path(__file__).parent))

from services.document_parser import parse_to_markdown
from services.ai_scorer import score_tz
from dotenv import load_dotenv

load_dotenv()

async def main():
    test_file = Path(r"C:\Users\Ali\Desktop\BitUnionTeam AI\ТЗ Цифровой полигон.docx")
    
    if not test_file.exists():
        print(f"❌ Тестовый файл {test_file} не найден!")
        return

    print("📄 Парсинг файла...")
    with open(test_file, "rb") as f:
        file_bytes = f.read()
    
    try:
        markdown = parse_to_markdown(file_bytes, test_file.name)
        print(f"✅ Успешный парсинг. Длина документа: {len(markdown)} символов")
    except Exception as e:
        print(f"❌ Ошибка парсинга: {e}")
        return

    print(f"\n🧠 Запуск скоринга через: {os.getenv('LLM_PROVIDER')} ...")
    try:
        result = await score_tz(markdown)
        print("\n\n" + "="*50)
        print("🎯 РЕЗУЛЬТАТ АУДИТА:")
        print("="*50)
        print(f"Итоговый балл: {result.total_score} / 100")
        print(f"Оценка (Грейд): {result.grade}")
        print("\n📊 Критерии:")
        for c in result.criteria:
            print(f"  - {c.name}: {c.score}/{c.max_score} ({c.reasoning})")
        print("\n⚠️ Ошибки:")
        for e in result.critical_errors:
            print(f"  - {e}")
        print("="*50)
        print(f"Успех! Скрипт отработал корректно. Тестовый балл: {result.total_score}")
    except Exception as e:
        print(f"❌ Ошибка скоринга: {e}")

if __name__ == "__main__":
    asyncio.run(main())
