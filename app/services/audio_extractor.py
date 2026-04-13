from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


class AudioExtractionError(RuntimeError):
    """Raised when ffmpeg or ffprobe fail to process the uploaded media."""


@dataclass(frozen=True)
class ExtractionResult:
    output_path: Path
    media_type: str
    filename: str


def _run_command(command: list[str]) -> None:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip() or "Unknown ffmpeg error"
        raise AudioExtractionError(stderr)


def _probe_audio_codec(input_path: Path, ffprobe_path: str) -> str:
    command = [
        ffprobe_path,
        "-v",
        "error",
        "-select_streams",
        "a:0",
        "-show_entries",
        "stream=codec_name",
        "-of",
        "json",
        str(input_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip() or "Unable to inspect media"
        raise AudioExtractionError(stderr)

    payload = json.loads(completed.stdout or "{}")
    streams = payload.get("streams") or []
    if not streams:
        raise AudioExtractionError("No audio stream was found in the uploaded file")

    codec_name = streams[0].get("codec_name")
    if not codec_name:
        raise AudioExtractionError("Unable to detect the audio codec")
    return str(codec_name).lower()


def _preserve_extension(codec_name: str) -> tuple[str, str]:
    return ".wav", "audio/wav"


def extract_audio_file(
    input_path: Path,
    output_dir: Path,
    ffmpeg_path: str,
    ffprobe_path: str,
) -> ExtractionResult:
    output_dir.mkdir(parents=True, exist_ok=True)

    if shutil.which(ffmpeg_path) is None:
        raise AudioExtractionError(f"ffmpeg executable was not found: {ffmpeg_path}")
    if shutil.which(ffprobe_path) is None:
        raise AudioExtractionError(f"ffprobe executable was not found: {ffprobe_path}")

    output_stem = input_path.stem or "audio"

    codec_name = _probe_audio_codec(input_path, ffprobe_path)
    extension, media_type = _preserve_extension(codec_name)
    output_path = output_dir / f"{output_stem}{extension}"
    command = [
        ffmpeg_path,
        "-y",
        "-i",
        str(input_path),
        "-map",
        "0:a:0",
        "-vn",
        "-c:a",
        "pcm_s16le",
        str(output_path),
    ]
    _run_command(command)
    return ExtractionResult(output_path=output_path, media_type=media_type, filename=output_path.name)
