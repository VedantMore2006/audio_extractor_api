# API Usage

## Base URL

When running locally:

```text
http://localhost:8000
```

## Endpoints

### GET /v1/health

Returns a simple health check response.

### POST /v1/extract-audio

Accepts a multipart file upload and returns an audio file.

## Request

- Content type: `multipart/form-data`
- Field name: `file`
- File type: video file such as MP4, MOV, MKV, WEBM, AVI, or similar formats supported by ffmpeg
- Optional query parameter: `output_format`

### `output_format`

- `original`: preserves the original audio codec without re-encoding and returns a Matroska audio file when needed for compatibility
- `wav`: converts the audio to WAV using PCM 16-bit encoding

## Response

- Success: `200 OK`
- Body: downloaded audio file
- Failure: `400 Bad Request` if the file has no audio stream or ffmpeg cannot process it
- Failure: `413 Payload Too Large` if the upload exceeds the configured size limit

## curl examples

### Extract audio while preserving the original codec

```bash
curl -X POST "http://localhost:8000/v1/extract-audio?output_format=original" \
  -F "file=@/path/to/video.mp4" \
  --output extracted-audio.mka
```

### Convert the audio to WAV

```bash
curl -X POST "http://localhost:8000/v1/extract-audio?output_format=wav" \
  -F "file=@/path/to/video.mp4" \
  --output extracted-audio.wav
```

## Environment variables

- `APP_NAME`: service display name
- `APP_VERSION`: application version
- `API_PREFIX`: route prefix, default `/v1`
- `LOG_LEVEL`: logging level
- `MAX_UPLOAD_MB`: maximum upload size in megabytes
- `DEFAULT_OUTPUT_FORMAT`: default output format, `original` or `wav`
- `CORS_ORIGINS`: comma-separated list of allowed origins or `*`
- `FFMPEG_PATH`: ffmpeg executable path
- `FFPROBE_PATH`: ffprobe executable path
