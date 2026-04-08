import structlog
from fastapi import Request, Response
from uuid_extensions import uuid7

logger = structlog.get_logger()


async def structlog_middleware(request: Request, call_next):
    """
    Middleware для внедрения request_id (UUID7) в контекст логов.
    """
    request_id = str(uuid7())

    with structlog.contextvars.bound_contextvars(request_id=request_id):
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
