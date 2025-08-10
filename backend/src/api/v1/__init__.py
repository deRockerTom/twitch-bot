from fastapi import APIRouter

from .health import health_router
from .tokens import tokens_router

v1_router = APIRouter()

v1_router.include_router(
    health_router,
    prefix="/health",
    tags=["health"],
)

v1_router.include_router(
    tokens_router,
    prefix="/tokens",
    tags=["tokens"],
)
