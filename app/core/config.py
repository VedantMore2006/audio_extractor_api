from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_NAME = "Audio Extractor API"
APP_VERSION = "1.0.0"
API_PREFIX = "/v1"
MAX_UPLOAD_BYTES = 500 * 1024 * 1024
MAX_REQUEST_BYTES = 520 * 1024 * 1024
DEFAULT_OUTPUT_MIME = "audio/wav"
DEFAULT_OUTPUT_EXTENSION = ".wav"
FFMPEG_PATH = "ffmpeg"
FFPROBE_PATH = "ffprobe"
ALLOWED_ORIGINS = ["*"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_key: str = ""

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, value: str) -> str:
        return value.strip()

    @property
    def api_key_enabled(self) -> bool:
        return bool(self.api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
