from pydantic import BaseModel
from enum import Enum


class Status(str, Enum):
    """
    Статусы обработки вопроса.
    """
    ERROR = "error"
    RUNNING = "running"
    DONE = "done"         

class QuestionCreate(BaseModel):
    text: str
    document_id: str

class QuestionOut(BaseModel):
    text: str
    document: str
    status: Status
    answer_text: str | None = None