from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.settings import settings

upload_router = APIRouter(prefix="/uploads")

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@upload_router.post("/")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in settings.ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only text files are supported (txt/md/json).",
        )

    safe_name = f"{uuid4()}-{file.filename}"
    target = (UPLOAD_DIR / safe_name).resolve()

    content = await file.read()
    target.write_bytes(content)

    return {
        "file_path": str(target),
        "filename": file.filename,
        "content_type": file.content_type,
    }

