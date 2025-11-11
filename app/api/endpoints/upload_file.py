# app/api/endpoints/upload_file.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import json
import tempfile

from app.core.utils import extract_text, generate_id, clean_text
from app.core.config import settings

router = APIRouter(prefix="/storage/files", tags=["Файлы"])

FILES_JSON_PATH = Path(settings.FILES_JSON_PATH)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # 1) Обработка загруженного файла
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Ожидается .docx")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            temp_path = Path(tmp.name)
            tmp.write(await file.read())
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось сохранить файл")

    # 3) Парсинг текста из .docx
    try:
        text = extract_text(str(temp_path))
        cleaned_text = clean_text(text)
    except Exception as e:
        temp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Ошибка парсинга файла: {e}")

    # Стираем временный файл
    temp_path.unlink(missing_ok=True)

    # 4) Генерация id файла
    file_id = generate_id()

    # 5) Сохранение текста в files.json как JSON-объект
    if FILES_JSON_PATH.exists():
        try:
            data = json.loads(FILES_JSON_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}

    # структура: { "<file_id>": { "text": "<parsed text>" } }
    data[file_id] = {"text": cleaned_text}

    FILES_JSON_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 6) Эндпоинт возвращает id файла
    return {"file_id": file_id}
