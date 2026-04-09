"""
Главный роутер API версии v1.

Агрегирует все эндпоинты приложения и подключает их к основному маршруту.
Используется для централизованного управления версиями API.
"""

from fastapi import APIRouter

from backend.app.api.v1.endpoints import message

api_router = APIRouter()
api_router.include_router(message.router, tags=["Message"])
