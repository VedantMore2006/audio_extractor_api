#!/bin/sh
set -eu

exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 1 \
  --limit-concurrency 20 \
  --timeout-keep-alive 5
