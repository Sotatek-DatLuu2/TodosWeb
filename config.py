from typing import List, Optional

from pydantic import EmailStr, Field

from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict



class ServerEnv(StrEnum):
    LOCAL = 'LOCAL'
    DEV = 'DEV'
    STAGING = 'STAGING'
    PRODUCTION = 'PRODUCTION'

    @property
    def is_debug(self) -> bool:
        return self in (self.LOCAL, self.STAGING, self.DEV)

    @property
    def is_testing(self) -> bool:
        return self == self.LOCAL

    @property
    def is_deployed(self) -> bool:
        return self in (self.STAGING, self.PRODUCTION)


class CustomBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class Config(CustomBaseSettings):
    ENVIRONMENT: ServerEnv = ServerEnv.LOCAL
    SECRET_KEY: str
    EMAIL_ADDRESS: EmailStr
    EMAIL_PASSWORD: str
    SMTP_HOST: str
    SMTP_PORT: int
    DATABASE_URL: str

    DEFAULT_ADMIN_USERNAME: str
    DEFAULT_ADMIN_EMAIL: EmailStr
    DEFAULT_ADMIN_FIRST_NAME: str
    DEFAULT_ADMIN_LAST_NAME: str
    DEFAULT_ADMIN_PASSWORD: str
    DEFAULT_ADMIN_PHONE_NUMBER: str

    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],  # Giá trị mặc định cho phát triển
        description="Danh sách các nguồn gốc (origins) được phép cho CORS."
    )
    CORS_ORIGIN_REGEX: Optional[str] = Field(
        default=None,
        description="Regex cho các nguồn gốc được phép cho CORS."
    )
    CORS_HEADERS: List[str] = Field(
        default=["Content-Type", "Authorization"],
        description="Danh sách các HTTP headers được phép cho CORS."
    )

settings = Config()