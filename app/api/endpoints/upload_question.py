from pathlib import Path
import json

from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.core.utils import generate_id, load_storage, save_storage, logger
from app.core.config import settings
from app.models.base import QuestionCreate, Status, QuestionOut
from app.services.questions import process_question



router = APIRouter(prefix="/storage/questions", tags=["Вопросы"])

QUESTIONS_JSON_PATH = Path(settings.QUESTIONS_JSON_PATH)

@router.post("/", response_model=dict)
async def upload_question(payload: QuestionCreate, background_tasks: BackgroundTasks):
    try:
        questions = load_storage(QUESTIONS_JSON_PATH)

        question_id = generate_id()
        logger.info(f"Создание нового вопроса {question_id} для документа {payload.document_id}")

        questions[question_id] = {
            "text": payload.text,
            "document": payload.document_id,
            "status": Status.RUNNING.value,
            "answer_text": None,
        }
        save_storage(QUESTIONS_JSON_PATH, questions)
        logger.debug(f"Вопрос {question_id} сохранен в хранилище")

        # переход к генерации ответа на вопрос в фоновом режиме после возврата id вопроса
        background_tasks.add_task(process_question, QUESTIONS_JSON_PATH, question_id)
        logger.debug(f"Фоновая задача для вопроса {question_id} добавлена в очередь")

        return {"question_id": question_id}
    except Exception as e:
        logger.error(
            f"Ошибка при создании вопроса для документа {payload.document_id}: "
            f"{type(e).__name__}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Не удалось создать вопрос: {str(e)}"
        ) from e


@router.get("/{question_id}", response_model=QuestionOut)
async def get_question(question_id: str):
    try:
        questions = load_storage(QUESTIONS_JSON_PATH)

        if question_id not in questions:
            logger.warning(f"Запрос несуществующего вопроса {question_id}")
            raise HTTPException(status_code=404, detail="Вопрос не найден")

        data = questions[question_id]
        logger.debug(f"Возврат данных вопроса {question_id}, статус: {data.get('status')}")

        return QuestionOut(
            text=data["text"],
            document=data["document"],
            status=Status(data["status"]),
            answer_text=data.get("answer_text"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Ошибка при получении вопроса {question_id}: {type(e).__name__}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Не удалось получить вопрос: {str(e)}"
        ) from e