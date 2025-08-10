from db import db_client
from fastapi import APIRouter

from shared import Token

tokens_router = APIRouter()


@tokens_router.get("/", response_model=list[Token])
async def get_tokens():
    """
    Get all subscribed users from database
    """
    tokens = await db_client.tokens.get()
    return tokens
