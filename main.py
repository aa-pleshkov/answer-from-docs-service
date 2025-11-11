"""Точка входа в приложение FastAPI."""

from fastapi import FastAPI
import uvicorn
from pathlib import Path

from app.api.endpoints.upload_file import router as upload_file_router
from app.api.endpoints.upload_question import router as upload_question_router
from app.core.config import settings
from app.core.utils import logger, save_storage


def create_application() -> FastAPI:
    """Приложение FastAPI."""
    application = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description="Сервис для ответов на вопросы по документам через LLM",
    )

    application.include_router(upload_file_router)
    application.include_router(upload_question_router)

    @application.get("/healthcheck")
    def health_check() -> dict[str, str]:
        return {"status": "healthy", "service": settings.APP_TITLE}

    @application.on_event("startup")
    def startup_message() -> None:
        """Вывод адреса для доступа к сервису."""
        import os
        is_docker = os.path.exists("/.dockerenv")
        if is_docker:
            logger.info("=" * 60)
            logger.info("Сервис запущен и доступен по адресу:")
            logger.info("  http://localhost:8000")
            logger.info("  http://127.0.0.1:8000")
            logger.info("Документация API: http://localhost:8000/docs")
            logger.info("=" * 60)
        else:
            logger.info("=" * 60)
            logger.info(f"Сервис запущен и доступен по адресу:")
            logger.info(f"  http://{settings.HOST}:{settings.PORT}")
            logger.info(f"Документация API: http://{settings.HOST}:{settings.PORT}/docs")
            logger.info("=" * 60)

    @application.on_event("shutdown")
    def cleanup_storage() -> None:
        """Очистка JSON-хранилищ при завершении приложения."""
        for storage_path in (
            Path(settings.FILES_JSON_PATH),
            Path(settings.QUESTIONS_JSON_PATH),
        ):
            try:
                if storage_path.exists():
                    save_storage(storage_path, {})
                    logger.info(f"Очищено хранилище {storage_path}")
            except Exception as exc:
                logger.warning(
                    "Не удалось очистить хранилище %s: %s",
                    storage_path,
                    exc,
                )

    return application


app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )