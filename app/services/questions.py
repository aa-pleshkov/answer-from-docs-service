# app/services/questions.py
from app.core.utils import load_storage, save_storage, logger
from app.models.base import Status
from pathlib import Path
from app.services.llm import LLM
from app.core.config import settings

llm = LLM()
FILES_PATH = Path(settings.FILES_JSON_PATH)

def process_question(questions_path: Path, question_id: str):
    questions = load_storage(questions_path)
    q = questions.get(question_id)
    if not q:
        logger.warning(f"Вопрос с ID {question_id} не найден в хранилище")
        return

    q["status"] = Status.RUNNING.value
    save_storage(questions_path, questions)
    logger.info(f"Начата обработка вопроса {question_id}: {q.get('text', '')[:50]}...")

    try:
        document_text = "Текст документа недоступен"
        document_id = q["document"]
        documents = load_storage(FILES_PATH)
        document_data = documents.get(document_id)
        if document_data:
            document_text = document_data.get("text") or document_text
        else:
            logger.warning(f"Документ {document_id} не найден в {FILES_PATH}")

        messages = llm.prompt_builder(q['text'], document_text)
        logger.debug(f"Промпт для LLM сформирован корректно для вопроса {question_id}")

        llm_response = llm.generate_response(messages)
        logger.info(f"Ответ от LLM модели получен для вопроса {question_id}")

        questions = load_storage(questions_path)
        q = questions.get(question_id)
        if not q:
            logger.warning(f"Вопрос {question_id} был удален во время обработки")
            return

        q["status"] = Status.DONE.value

        q["answer_text"] = llm_response
        save_storage(questions_path, questions)

        logger.info(f"Вопрос {question_id} успешно обработан")

    except Exception as e:
        logger.error(
            f"Ошибка при обработке вопроса {question_id}: {type(e).__name__}: {str(e)}",
            exc_info=True
        )
        try:
            questions = load_storage(questions_path)
            q = questions.get(question_id)
            if not q:
                logger.warning(f"Вопрос {question_id} не найден при обработке ошибки")
                return

            q["status"] = Status.ERROR.value
            save_storage(questions_path, questions)

            logger.info(f"Статус вопроса {question_id} обновлен на ERROR")

        except Exception as save_error:
            logger.critical(
                f"Критическая ошибка при сохранении статуса ERROR для вопроса {question_id}: "
                f"{type(save_error).__name__}: {str(save_error)}",
                exc_info=True
            )
