from __future__ import annotations

import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import DEFAULT_OUTPUT_MIME, FFMPEG_PATH, FFPROBE_PATH, MAX_UPLOAD_BYTES, Settings, get_settings
from app.services.audio_extractor import AudioExtractionError, extract_audio_file

router = APIRouter()
logger = logging.getLogger(__name__)


async def require_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    settings: Settings = Depends(get_settings),
) -> None:
    if not settings.api_key_enabled:
        return

    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


async def _save_upload(upload_file: UploadFile, destination: Path, max_bytes: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    bytes_written = 0
    with destination.open("wb") as output_file:
        while True:
            chunk = await upload_file.read(1024 * 1024)
            if not chunk:
                break
            bytes_written += len(chunk)
            if bytes_written > max_bytes:
                raise HTTPException(status_code=413, detail="File exceeds the configured upload size limit")
            output_file.write(chunk)


def _cleanup_directory(directory: str) -> None:
    if os.path.isdir(directory):
        shutil.rmtree(directory, ignore_errors=True)


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/extract-audio")
async def extract_audio(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File(...)],
    _: Annotated[None, Depends(require_api_key)] = None,
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A video file is required")

    temp_dir = tempfile.mkdtemp(prefix="audio-extractor-")
    temp_root = Path(temp_dir)
    input_suffix = Path(file.filename).suffix or ".upload"
    input_path = temp_root / f"input{input_suffix}"

    try:
        logger.info("Receiving upload filename=%s content_type=%s", file.filename, file.content_type)
        await _save_upload(file, input_path, MAX_UPLOAD_BYTES)
    except HTTPException:
        logger.warning("Upload rejected filename=%s", file.filename)
        background_tasks.add_task(_cleanup_directory, temp_dir)
        raise
    finally:
        await file.close()

    try:
        result = extract_audio_file(
            input_path=input_path,
            output_dir=temp_root,
            ffmpeg_path=FFMPEG_PATH,
            ffprobe_path=FFPROBE_PATH,
        )
    except AudioExtractionError as exc:
        logger.exception("Audio extraction failed filename=%s", file.filename)
        background_tasks.add_task(_cleanup_directory, temp_dir)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected extraction error filename=%s", file.filename)
        background_tasks.add_task(_cleanup_directory, temp_dir)
        raise HTTPException(status_code=500, detail="Unexpected error while extracting audio") from exc

    logger.info("Audio extraction completed filename=%s output=%s", file.filename, result.filename)
    background_tasks.add_task(_cleanup_directory, temp_dir)
    return FileResponse(
        path=result.output_path,
        media_type=DEFAULT_OUTPUT_MIME,
        filename=result.filename,
        background=background_tasks,
    )
