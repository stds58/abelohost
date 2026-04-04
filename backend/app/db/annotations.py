from datetime import datetime
from typing import Annotated
from uuid import UUID

from sqlalchemy import TIMESTAMP, UUID as SQLAlchemyUUID, text
from sqlalchemy.orm import mapped_column
from uuid_extensions import uuid7

UUIDPk = Annotated[
    UUID,
    mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
        server_default=None,
    ),
]

CreatedAt = Annotated[
    datetime,
    mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
    ),
]
