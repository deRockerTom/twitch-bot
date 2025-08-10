from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration settings for the bot.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # MongoDB configuration
    MONGO__DB: str = "twitch-bot"
    MONGO__HOST: str = "localhost"
    MONGO__PORT: int = 27017


BACKEND_SERVER_SETTINGS = Settings()
