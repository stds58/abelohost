"""
Системный роутер API.
Агрегирует все эндпоинты healthcheck
"""

from fastapi import APIRouter

from backend.app.api.system.endpoints.db import router as db_router
from backend.app.api.system.endpoints.health import router as health_router
from backend.app.core.config import settings

api_router = APIRouter()
api_router.include_router(health_router, tags=["Healthcheck"])
if settings.DEBUG_MODE:
    api_router.include_router(db_router, tags=["Check_db"])
