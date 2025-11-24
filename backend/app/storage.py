import os
import secrets
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from .config import get_settings

settings = get_settings()


def ensure_upload_dir() -> Path:
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


def save_image(file: Optional[UploadFile]) -> Optional[str]:
    if not file:
        return None
    ensure_upload_dir()
    filename = Path(file.filename).name
    suffix = Path(filename).suffix.lower()
    safe_name = f"{secrets.token_hex(8)}{suffix}"
    dest = Path(settings.upload_dir) / safe_name
    with dest.open("wb") as buffer:
        buffer.write(file.file.read())
    return str(dest)
