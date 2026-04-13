# API Usage

## Base URL

When running locally:

```text
http://localhost:8012
```

## Endpoints

### GET /v1/health

Returns a simple health check response.

### POST /v1/extract-audio

Accepts a multipart video upload and returns a WAV file.

If `API_KEY` is configured, include the `X-API-Key` header in the request.

## Behavior

- Input: any video file supported by ffmpeg.
- Output: WAV audio only.
- Maximum upload size: 500 MB.
- Response style: direct file download.
- No separate retrieval endpoint is used.

## Request

- Content type: `multipart/form-data`
- Field name: `file`
- File type: any video file format supported by ffmpeg, including MP4, MKV, WEBM, MOV, AVI, M4V, FLV, WMV, TS, and more
- Optional header: `X-API-Key`

## Response

- Success: `200 OK`
- Body: downloaded audio file
- Failure: `400 Bad Request` if the file has no audio stream or ffmpeg cannot process it
- Failure: `401 Unauthorized` if the API key is missing or invalid
- Failure: `413 Payload Too Large` if the upload exceeds the configured size limit
- Failure: `500 Internal Server Error` if an unexpected server error occurs

## curl examples

### Extract audio from MP4

```bash
curl -X POST "http://localhost:8012/v1/extract-audio" \
  -F "file=@/path/to/video.mp4" \
  --output extracted-audio.wav
```

### Extract audio from MKV with API key

```bash
curl -X POST "http://localhost:8012/v1/extract-audio" \
  -F "file=@/path/to/video.mp4" \
  -H "X-API-Key: your-secret-key" \
  --output extracted-audio.wav
```

### Extract audio from WEBM

```bash
curl -X POST "http://localhost:8012/v1/extract-audio" \
  -F "file=@/path/to/video.webm" \
  --output extracted-audio.wav
```

### Extract audio from MOV

```bash
curl -X POST "http://localhost:8012/v1/extract-audio" \
  -F "file=@/path/to/video.mov" \
  --output extracted-audio.wav
```

### Extract audio from AVI

```bash
curl -X POST "http://localhost:8012/v1/extract-audio" \
  -F "file=@/path/to/video.avi" \
  --output extracted-audio.wav
```

## Environment variables

- `API_KEY`: optional API key required via the `X-API-Key` header

## Troubleshooting

- If the request is rejected with `413`, the file is larger than 500 MB.
- If you get `400`, the input may be damaged, encrypted, or missing an audio stream.
- If the container healthcheck fails, verify that ffmpeg is installed inside the image and the service is listening on port 8012.
