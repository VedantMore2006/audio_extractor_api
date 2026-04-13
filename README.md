# Audio Extractor API

FastAPI service that accepts a video upload and returns the extracted audio.

## What it does

- Extracts audio from an uploaded video file.
- Preserves the original audio codec by default without re-encoding.
- Can also convert the audio to WAV on demand.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Run with Docker

```bash
docker compose up --build
```

## Configuration

Copy `.env.example` to `.env` and adjust the values as needed.

## API docs

See [API_USAGE.md](API_USAGE.md) for endpoints, request formats, and curl examples.
