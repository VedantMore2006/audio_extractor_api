# Audio Extractor API

FastAPI service that accepts a video upload and returns only the extracted audio in WAV format.

## What it does

- Accepts a video file upload and extracts the audio track.
- Always returns a WAV file.
- Keeps the API surface small: only `GET /v1/health` and `POST /v1/extract-audio`.
- Supports any video format ffmpeg can read, including MP4, MKV, WEBM, MOV, AVI, and M4V.
- Uses one optional secret: `API_KEY` in the `X-API-Key` header.

## Request flow

1. Client uploads a video to `POST /v1/extract-audio`.
1. The service validates the request size and optional API key.
1. ffmpeg extracts the audio and encodes it as WAV.
1. The response returns the WAV file directly as a download.

There is no separate storage or retrieval endpoint. The service is designed for direct request/response use behind Docker or a VPS.

## Endpoints

### GET /v1/health

Returns a basic health response for container and load balancer checks.

### POST /v1/extract-audio

Accepts a multipart video upload and returns a WAV file.

## Authentication

If `API_KEY` is set in the environment, clients must send the same value in the `X-API-Key` header.

If `API_KEY` is empty, the endpoint is public.

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

## Production notes

- Upload limit is hardcoded to 500 MB.
- The container includes a Docker healthcheck that hits `/v1/health`.
- The runtime script enables Uvicorn worker and concurrency settings for production.
- Only `API_KEY` is read from the environment.

## API docs

See [API_USAGE.md](API_USAGE.md) for request formats, curl examples, API key usage, and troubleshooting.
