# 🤖 AI-система анализа и улучшения Технических Заданий (ТЗ)

> **Хакатон «НТЦ LAB: Хакатон конкурентных решений»**  
> Даты: 14–15 апреля 2025 г. | Формат: 24-часовой хакатон  
> Команда: **BitUnion**

---

## 📌 О проекте

Интеллектуальная система на базе LLM (Gemini / GPT-4o / Claude), предназначенная для автоматизированного анализа, оценки и улучшения Технических Заданий научных проектов в рамках программно-целевого финансирования МОН РК.

Система выявляет структурные ошибки, расплывчатые формулировки, отсутствующие KPI и несоответствие требованиям грантового финансирования — и формирует детальный аудит-отчёт с конкретными рекомендациями.

---

## 🏗 Архитектура системы

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)               │
│   UploadPage → DashboardPage (ScoreGauge, CriteriaRadar) │
└───────────────────────┬─────────────────────────────────┘
                        │  REST API
┌───────────────────────▼─────────────────────────────────┐
│                  Backend (FastAPI)                        │
│  POST /api/upload  ─►  document_parser  ─►  ai_scorer   │
└───────────────────────┬─────────────────────────────────┘
                        │
            ┌───────────▼───────────┐
            │  LLM Provider (env)   │
            │  gemini / openai /    │
            │  anthropic / ollama   │
            └───────────────────────┘
```

### Компоненты технологического стека

| Уровень | Технологии |
|---|---|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Recharts |
| **Backend** | Python 3.11, FastAPI, Pydantic v2, python-docx, PyMuPDF |
| **AI / LLM** | Google Gemini 1.5 Pro, OpenAI GPT-4o, Anthropic Claude, Ollama (offline) |
| **NLP** | Структурный парсинг DOCX/PDF, Few-Shot prompting, JSON-mode |
| **Инфраструктура** | Docker, Docker Compose |

---

## ✨ Ключевые возможности

- 📄 **Загрузка ТЗ** в форматах PDF, DOCX, TXT
- 🔍 **Структурный анализ** — автоматическая проверка наличия 5 обязательных разделов по официальному шаблону МОН РК
- 🎯 **Оценка по 7 критериям** (точно по `Оценка_ТЗ_шаблон.xlsx`):
  - Стратегическая релевантность (20%)
  - Цель и задачи (10%)
  - Научная новизна (15%)
  - Практическая применимость (20%)
  - Ожидаемые результаты (15%)
  - Соц-экономический эффект (10%)
  - Реализуемость (10%)
- 📊 **Визуализация** — интерактивный спидометр (ScoreGauge) и радарная диаграмма критериев
- 💡 **Рекомендации** — конкретные исправления с улучшенным фрагментом ТЗ в Markdown
- 🌐 **Мультипровайдерность** — переключение между LLM через `.env`

---

## 🚀 Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone <repo-url>
cd "BitUnionTeam AI"
```

### 2. Настройте Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env — укажите GOOGLE_API_KEY и LLM_PROVIDER=gemini
```

### 3. Запустите Backend

```bash
# Из папки backend:
uvicorn main:app --reload --port 8000
```

### 4. Настройте и запустите Frontend

```bash
cd frontend
npm install
npm run dev
# Откройте http://localhost:5173
```

### 5. Docker (опционально)

```bash
# Из корня проекта:
docker-compose up --build
```

---

## ⚙️ Переменные окружения (`backend/.env`)

```env
# Выбор LLM-провайдера: gemini | openai | anthropic | ollama
LLM_PROVIDER=gemini

# Google Gemini
GOOGLE_API_KEY=your_key_here
GOOGLE_MODEL=gemini-1.5-pro

# OpenAI (если LLM_PROVIDER=openai)
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o

# Anthropic Claude (если LLM_PROVIDER=anthropic)
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Ollama локальный (если LLM_PROVIDER=ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b
```

---

## 📂 Структура проекта

```
BitUnionTeam AI/
├── backend/
│   ├── main.py                  # FastAPI приложение
│   ├── requirements.txt
│   ├── .env.example
│   ├── routers/
│   │   ├── upload.py            # POST /api/upload — основной эндпоинт
│   │   └── health.py            # GET /health
│   └── services/
│       ├── ai_scorer.py         # LLM-оценщик (Pydantic схема + системный промпт)
│       └── document_parser.py   # Парсер DOCX/PDF → Markdown + структурный анализ
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── UploadPage.tsx   # Страница загрузки ТЗ
│   │   │   └── DashboardPage.tsx # Страница результатов
│   │   ├── components/
│   │   │   ├── ScoreGauge.tsx   # Спидометр итогового балла
│   │   │   └── CriteriaRadar.tsx # Радарная диаграмма критериев
│   │   ├── api.ts               # HTTP-клиент к backend
│   │   └── types.ts             # TypeScript типы
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## 🧠 Техническое решение (для жюри)

### AI-логика (`ai_scorer.py`)

**Системный промпт** реализует:
- **Few-Shot обучение** на реальном примере «ТЗ Цифровой полигон» (Strong Smart Grid, оценка 90+/100)
- **Строгую схему** оценки, точно соответствующую официальному `Оценка_ТЗ_шаблон.xlsx`
- **Формулу итогового балла**: `score = Σ(критерий_i × вес_i)` где веса взяты напрямую из XLSX
- **Правила штрафов** за отсутствие конкретных пунктов стратегических документов, расплывчатые цели и KPI без цифр

**Pydantic v2 схема** гарантирует:
- Ровно 7 критериев в строгом порядке
- Автоматический пересчёт `total_score` (защита от галлюцинаций LLM)
- Автоматическое выставление буквенной оценки A/B/C/D/F

### Структурный анализ (`document_parser.py`)

Функция `check_tz_structure()` проверяет наличие 5 обязательных разделов по официальному шаблону МОН РК и **добавляет отчёт в начало** текста **до** передачи в LLM — это позволяет модели сразу знать, каких разделов нет.

---

## 👥 Команда BitUnion

| Роль | Задача |
|---|---|
| Backend Engineer | FastAPI, ai_scorer, document_parser |
| Frontend Engineer | React UI, DashboardPage, визуализация |
| AI/Prompt Engineer | Системный промпт, Few-Shot, Pydantic схема |

---

## 📄 Лицензия

MIT License — открытый исходный код для академического и коммерческого использования.
