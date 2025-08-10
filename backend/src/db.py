from config import BACKEND_SERVER_SETTINGS

from shared import DatabaseClient

db_client = DatabaseClient(
    host=BACKEND_SERVER_SETTINGS.MONGO__HOST,
    port=BACKEND_SERVER_SETTINGS.MONGO__PORT,
    database_name=BACKEND_SERVER_SETTINGS.MONGO__DB,
)
