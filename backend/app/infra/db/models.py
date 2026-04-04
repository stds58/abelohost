from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.domain.entities.message import Message as MessageDomain


class Message(Base):
    """A database table for storing message data."""

    __tablename__ = "messages"

    text: Mapped[str] = mapped_column(nullable=False)

    def to_domain(self) -> MessageDomain:
        return MessageDomain.from_dict(
            {
                "id": str(self.id),
                "created_at": self.created_at.isoformat(),
                "text": self.text,
            }
        )

    def __repr__(self):
        return f"<Message(uuid={self.id}, created_at='{self.created_at}')>"
