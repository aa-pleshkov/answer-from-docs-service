# Answer from Docs Service

Сервис для ответов на вопросы по документам через LLM.

## Структура проекта

```
answer_from_docs_service/
├── main.py              # Точка входа FastAPI
├── requirements.txt     # Зависимости Python
├── .env                 # Переменные окружения (создать самостоятельно)
├── .gitignore
├── README.md
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── routes_files.py
│   │       └── routes_questions.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── utils.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm.py
│   │   ├── prompt_builder.py
│   │   ├── summarizer.py
│   │   ├── status_tracker.py
│   │   └── queue.py
│   └── models/
│       ├── __init__.py
│       └── dto.py
└── static/              # Файлы для Swagger (опционально)

```

## Установка и запуск

1. Создать виртуальное окружение:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

3. Запустить сервер:
```bash
uvicorn main:app --reload
```

4. Открыть документацию:
http://localhost:8000/docs


## Особенности

- При остановке приложения содержимое `storage/files.json` и `storage/questions.json` очищается автоматически.

## Тесты

```bash
pytest
```

## Запуск в Docker

1. Скопируйте файл окружения:
   ```bash
   cp env.example .env
   ```
2. Укажите реальные значения переменных (минимум `LLM_API_KEY`).
3. Соберите и запустите контейнер:
   ```bash
   docker compose up --build
   ```
4. Откройте API на `http://localhost:8000/docs`.





