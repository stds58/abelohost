from fastapi import APIRouter

from backend.app.api.v1.endpoints import message

api_router = APIRouter()
api_router.include_router(message.router, prefix="/message", tags=["Message"])
