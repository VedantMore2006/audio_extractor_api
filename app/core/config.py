from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Audio Extractor API"
    app_version: str = "1.0.0"
    api_prefix: str = "/v1"
    log_level: str = "INFO"
    max_upload_mb: int = 200
    default_output_format: str = "original"
    cors_origins: str = "*"
    ffmpeg_path: str = "ffmpeg"
    ffprobe_path: str = "ffprobe"

    @field_validator("default_output_format")
    @classmethod
    def validate_default_output_format(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"original", "wav"}:
            raise ValueError("default_output_format must be 'original' or 'wav'")
        return normalized

    @field_validator("max_upload_mb")
    @classmethod
    def validate_max_upload_mb(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("max_upload_mb must be greater than zero")
        return value

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def allowed_origins(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
