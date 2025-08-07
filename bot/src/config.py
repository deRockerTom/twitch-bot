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

    # Bot configuration
    BOT_ID: str = "your_bot_id_here"  # Replace with your actual bot ID
    OWNER_ID: str = "your_owner_id_here"  # Replace with your actual owner ID
    CLIENT_ID: str = "your_client_id_here"  # Replace with your actual client ID
    CLIENT_SECRET: str = "your_client_secret_here"  # Replace with your actual client secret


BOT_SETTINGS = Settings()
