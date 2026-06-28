from typing import Optional

from environs import Env
from pydantic import Field
from pydantic_settings import BaseSettings

# environs kutubxonasidan foydalanib .env faylini o`qib olamiz
env = Env()
env.read_env()


# APP parametrlari
class AppSettings(BaseSettings):
    app_name: str = env.str("APP_NAME")
    app_url: str = env.str("APP_URL")
    secret_key: str = env.str("SECRET_KEY")
    algorithm: str = env.str("ALGORITHM")
    access_token_expire_minutes: int = env.int("ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = env.int("REFRESH_TOKEN_EXPIRE_DAYS")


# Baza ma`umotlari
class DatabaseSettings(BaseSettings):
    db_connection: str = env.str("DB_CONNECTION")
    db_host: str = env.str("DB_HOST")
    db_port: int = env.int("DB_PORT")
    db_database: str = env.str("DB_DATABASE")
    db_username: str = env.str("DB_USERNAME")
    db_password: Optional[str] = Field(default=env.str("DB_PASSWORD", None))
    db_charset: str = env.str("DB_CHARSET")


# AlembicSettings
class AlembicSettings(BaseSettings):
    ab_connection: str = env.str("DB_CONNECTION_ALEMBIC")

# SlackSettings
class SlackSettings(BaseSettings):
    slack_channel_url: str = env.str("SLACK_CHANNEL_URL")


# Settings barcha settingslar
class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    database: DatabaseSettings = DatabaseSettings()
    alembic: AlembicSettings = AlembicSettings()
    slack: SlackSettings = SlackSettings()
    static: str = env.str("STATIC")
    debug: bool = env.bool("DEBUG")


# Configa yuklash
config = Settings()