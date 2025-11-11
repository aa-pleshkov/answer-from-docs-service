# Answer from Docs Service

Сервис для ответов на вопросы по документам через LLM.

## Структура проекта

```
answer_from_docs_service/
├── main.py                    # Точка входа FastAPI, инициализация приложения
├── requirements.txt           # Зависимости Python
├── Dockerfile                 # Конфигурация Docker-образа
├── docker-compose.yml         # Конфигурация Docker Compose
├── env.example                # Пример файла с переменными окружения
├── .gitignore                 # Игнорируемые файлы для Git
├── README.md                  # Документация проекта
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       ├── upload_file.py      # API для загрузки .docx файлов и извлечения текста
│   │       └── upload_question.py  # API для создания вопросов и получения ответов
│   ├── core/
│   │   ├── config.py              # Настройки приложения (Pydantic Settings)
│   │   └── utils.py               # Утилиты: парсинг .docx, работа с JSON-хранилищем, генерация ID
│   ├── models/
│   │   └── base.py                # Pydantic модели: QuestionCreate, QuestionOut, Status
│   └── services/
│       ├── llm.py                 # Сервис для работы с LLM API (генерация ответов)
│       └── questions.py           # Обработка вопросов в фоновом режиме
├── prompts/
│   └── system.txt                 # Системный промпт для LLM
├── schemas/
│   └── answer_schema.json         # JSON-схема для структурированного ответа LLM
├── storage/
│   ├── files.json                 # JSON-хранилище загруженных документов
│   └── questions.json             # JSON-хранилище вопросов и ответов
└── tests/
    └── test_core_utils.py         # Тесты для утилит
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
   copy env.example .env
   ```
2. Укажите реальные значения переменных (минимум `LLM_API_KEY`).
3. Соберите и запустите контейнер:
   ```bash
   docker compose up --build
   ```
4. Откройте API на `http://localhost:8000/docs`.

### Проверка работоспособности

После запуска контейнера можно проверить функционал с помощью следующих curl-запросов:

**1. Загрузка документа (.docx файл):**
```bash
curl.exe -X POST "http://localhost:8000/storage/files/upload" -F "file=@C:\путь\до\файла.docx"
```
Возвращает `file_id` для использования в следующих запросах.

**2. Создание вопроса по документу:**
```bash
curl.exe -X POST "http://localhost:8000/storage/questions/" -H "Content-Type: application/json" -d "{\"text\": \"текст вопроса\", \"document_id\": \"id документа\"}"
```
Возвращает `question_id`. Обработка вопроса выполняется в фоновом режиме.

**3. Получение ответа на вопрос:**
```bash
curl.exe "http://localhost:8000/storage/questions/id вопроса"
```
Возвращает статус обработки (`running`, `done`, `error`) и ответ, если обработка завершена.





