from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Annotated, Literal

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from app.core.config import Settings, get_settings
from app.services.audio_extractor import AudioExtractionError, extract_audio_file

router = APIRouter()


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
    output_format: Annotated[str | None, Query(description="original or wav")] = None,
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A video file is required")

    temp_dir = tempfile.mkdtemp(prefix="audio-extractor-")
    temp_root = Path(temp_dir)
    input_suffix = Path(file.filename).suffix or ".upload"
    input_path = temp_root / f"input{input_suffix}"

    selected_output_format = (output_format or settings.default_output_format).strip().lower()

    try:
        await _save_upload(file, input_path, settings.max_upload_bytes)
    except HTTPException:
        background_tasks.add_task(_cleanup_directory, temp_dir)
        raise
    finally:
        await file.close()

    try:
        result = extract_audio_file(
            input_path=input_path,
            output_dir=temp_root,
            output_format=selected_output_format,
            ffmpeg_path=settings.ffmpeg_path,
            ffprobe_path=settings.ffprobe_path,
        )
    except AudioExtractionError as exc:
        background_tasks.add_task(_cleanup_directory, temp_dir)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    background_tasks.add_task(_cleanup_directory, temp_dir)
    return FileResponse(
        path=result.output_path,
        media_type=result.media_type,
        filename=result.filename,
        background=background_tasks,
    )
