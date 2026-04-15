# SOTA-2026: Умный скоринг Технических Заданий

> **AI-система автоматического аудита, улучшения и сопровождения ТЗ научных проектов**
> Хакатон НТЦ LAB | 14–15 апреля 2025 | Команда **BitUnion**

---

## Что умеет система

Пользователь загружает техническое задание в `DOCX`, `PDF`, `TXT` или `MD`, после чего система:

1. Парсит документ в Markdown.
2. Проверяет наличие обязательных разделов по шаблону ТЗ.
3. Оценивает документ по 7 критериям жюри.
4. Показывает критические ошибки и сильные стороны.
5. Генерирует улучшенный фрагмент ТЗ.
6. Позволяет скачать итоговый отчёт.
7. Сохраняет анализ в историю.
8. Даёт чат-ассистента по доработке документа.
9. Генерирует пример структуры ТЗ для ориентира.

---

## Актуальные возможности

- Drag-and-drop загрузка ТЗ.
- Проверка структуры документа.
- LLM-аудит по шкале `0–100`.
- История анализов с сохранением в `SQLite`.
- Регистрация и вход пользователей.
- Чат с AI-ассистентом по конкретному ТЗ.
- Генерация примера ТЗ.
- Скачивание улучшенного фрагмента и полного отчёта в Markdown.
- Поддержка нескольких LLM-провайдеров.

---

## Быстрый запуск

### Требования

- Python `3.12` рекомендуется на Windows.
- Node.js `18+`.
- API-ключ Groq, Gemini, OpenAI, Anthropic или локальная Ollama.

### Backend

```powershell
cd "backend"

py -3.12 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

copy .env.example .env
# Откройте backend/.env и заполните нужный ключ

uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

После запуска:

- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/api/health`

### Frontend

```powershell
cd "frontend"
npm install
npm run dev
```

После запуска откройте `http://localhost:5173`.

---

## Настройка LLM

По умолчанию проект настроен на **Groq**, так как он удобен для демо и не упирается в прежние лимиты Gemini.

Пример `backend/.env`:

```env
LLM_PROVIDER=groq

GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile

JWT_SECRET=replace-me-with-long-random-string
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
MAX_FILE_SIZE_MB=50
```

Поддерживаемые значения `LLM_PROVIDER`:

- `groq`
- `gemini`
- `openai`
- `anthropic`
- `ollama`

Если используете `ollama`, предварительно запустите локальную модель, например:

```powershell
ollama run qwen2.5:14b
```

---

## Demo Commands

Для быстрого показа в PyCharm или обычном PowerShell:

### Терминал 1 — API

```powershell
cd "C:\Users\Ali\Desktop\BitUnionTeam AI\backend"
.\.venv\Scripts\activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Терминал 2 — Frontend

```powershell
cd "C:\Users\Ali\Desktop\BitUnionTeam AI\frontend"
npm run dev
```

### Что показать жюри

1. Регистрация нового пользователя.
2. Вход в систему.
3. Загрузка слабого ТЗ.
4. Балл, радар и критические замечания.
5. Улучшенный фрагмент ТЗ.
6. Полный отчёт на скачивание.
7. Чат-ассистент.
8. История анализов.
9. Генерация примера ТЗ.

---

## Архитектура

### Общий поток

```text
Пользователь загружает файл
        ↓
[document_parser.py]
  DOCX/PDF/TXT/MD → Markdown
  Проверка обязательных разделов
        ↓
[ai_scorer.py]
  Системный промпт + текст ТЗ
  LLM → строгий JSON
        ↓
[TZAuditResult]
  Валидация схемы
  Пересчёт total_score
  Автоматический grade
        ↓
[React UI]
  Дашборд, история, чат, отчёт, пример ТЗ
        ↓
[SQLite]
  Сохранение истории анализов
```

### Ключевые backend-модули

- `backend/main.py` — инициализация FastAPI, CORS, роуты, БД.
- `backend/db.py` — SQLAlchemy engine и session.
- `backend/db_models.py` — пользователи и анализы.
- `backend/security.py` — хеширование паролей и JWT.
- `backend/deps.py` — текущий пользователь и зависимости.
- `backend/report_builder.py` — сборка итогового отчёта в Markdown.
- `backend/services/document_parser.py` — парсинг и структурная проверка.
- `backend/services/ai_scorer.py` — основной аудит ТЗ.
- `backend/services/assistant_llm.py` — чат и генерация примера ТЗ.

### Ключевые frontend-модули

- `frontend/src/App.tsx` — навигация между экранами.
- `frontend/src/pages/UploadPage.tsx` — загрузка и запуск анализа.
- `frontend/src/pages/DashboardPage.tsx` — результат анализа и отчёт.
- `frontend/src/pages/HistoryPage.tsx` — история анализов.
- `frontend/src/pages/LoginPage.tsx` / `RegisterPage.tsx` — auth.
- `frontend/src/components/ChatPanel.tsx` — AI-чат.
- `frontend/src/api.ts` — API-клиент.

---

## Критерии оценки

Система оценивает ТЗ по 7 критериям:

| Критерий | Вес | Что проверяется |
|---|---|---|
| Стратегическая релевантность | 20% | Привязка к госпрограммам и стратегиям |
| Цель и задачи | 10% | Измеримость и логичность |
| Научная новизна | 15% | Наличие нового подхода |
| Практическая применимость | 20% | Партнёры, пилоты, внедрение |
| Ожидаемые результаты | 15% | KPI и измеримые результаты |
| Соц-экономический эффект | 10% | Эффект в цифрах |
| Реализуемость | 10% | Бюджет, план, ресурсы |

Грейды:

| Балл | Оценка |
|---|---|
| 85–100 | A |
| 70–84 | B |
| 55–69 | C |
| 40–54 | D |
| < 40 | F |

---

## API

### Основные endpoint'ы

| Метод | URL | Назначение |
|---|---|---|
| `GET` | `/api/health` | Проверка статуса сервиса |
| `POST` | `/api/upload` | Загрузка файла и получение Markdown |
| `POST` | `/api/score` | Оценка Markdown-текста |
| `POST` | `/api/analyze` | Загрузка и анализ за один запрос |

### Auth и история

| Метод | URL | Назначение |
|---|---|---|
| `POST` | `/api/auth/register` | Регистрация |
| `POST` | `/api/auth/login` | Вход |
| `GET` | `/api/auth/me` | Текущий пользователь |
| `GET` | `/api/analyses` | Список анализов |
| `POST` | `/api/analyses` | Сохранить анализ |
| `GET` | `/api/analyses/{id}` | Получить анализ |
| `DELETE` | `/api/analyses/{id}` | Удалить анализ |
| `GET` | `/api/analyses/{id}/report` | Скачать отчёт |

### Дополнительно

| Метод | URL | Назначение |
|---|---|---|
| `POST` | `/api/chat` | Вопрос ассистенту |
| `POST` | `/api/example-tz` | Генерация примера ТЗ |
| `POST` | `/api/report/build` | Построение отчёта из результата |

---

## Demo-Ready Status

Проверено перед публикацией:

- backend импортируется без ошибок
- frontend собирается через `npm run build`
- GitHub-репозиторий обновлён
- Groq подключён как основной провайдер
- история и auth добавлены

Известное не критичное ограничение:

- production-бандл frontend крупный (`vite` предупреждает о размере чанка), но на работу демо это не влияет

---

## Репозиторий

GitHub: [ALStudentmay/BitUnionTeam-AI](https://github.com/ALStudentmay/BitUnionTeam-AI)

## Команда

BitUnion — хакатон НТЦ LAB: Хакатон конкурентных решений, 14–15 апреля 2025 г.
