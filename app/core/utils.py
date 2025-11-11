import logging
import uuid
from pathlib import Path
from docx2python import docx2python
import re
import json

# Настройка логгера
logger = logging.getLogger("answer_from_docs")
logger.setLevel(logging.INFO)

# Обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Формат логов: время, уровень, сообщение
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(formatter)

# Добавление обработчика к логгеру
if not logger.handlers:
    logger.addHandler(console_handler)


def generate_id() -> str:
    """
    Генерирует уникальный ID.
    
    Использует UUID4 для гарантии уникальности.
    
    Returns:
        str: Уникальный идентификатор
    """
    return str(uuid.uuid4())


def clean_text(text: str) -> str:
    """Очистка текста документа после парсинга."""

    try:
        if text is None:
            return ""
        s = text if isinstance(text, str) else str(text)
        s = (s.replace("\u00A0", " ")       
               .replace("\r", "\n")
               .replace("\u200b", ""))      
        s = re.sub(r"[ \t]+", " ", s)       
        s = re.sub(r" *\n+ *", "\n", s)     
        s = re.sub(r"\n{3,}", "\n\n", s)    
        s = re.sub(r"[\x00-\x08\x0b-\x1f]", "", s) 
        return s.strip()
    except Exception as e:
        raise RuntimeError(f"Очистка текста провалилась: {e}") from e

def extract_text(path: str) -> str:
    """Парсинг текста из .docx файла"""

    p = Path(path)

    if p.suffix.lower() != ".docx":
        raise ValueError("Поддерживаются только файлы с расширением .docx")

    try:
        with docx2python(str(p)) as doc:
            return doc.text or ""
    except FileNotFoundError:
        raise
    except PermissionError:
        raise
    except Exception as e:
        raise RuntimeError(f"Не удалось извлечь текст из файла '{p}': {e}") from e

def load_storage(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_storage(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )