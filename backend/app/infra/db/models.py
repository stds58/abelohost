"""
SQLAlchemy ORM модели для базы данных.
"""

from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.domain.entities.message import Message as MessageDomain


class Message(Base):
    """ORM модель таблицы messages.

    Attributes:
        text: Текст сообщения.
        id: Первичный ключ (UUID), наследуется от Base.
        created_at: Время создания, наследуется от Base.
    """

    __tablename__ = "messages"

    text: Mapped[str] = mapped_column(nullable=False)

    def to_domain(self) -> MessageDomain:
        """Конвертирует ORM модель в доменную сущность.

        Returns:
            MessageDomain: Доменная сущность Message.
        """
        return MessageDomain.from_dict(
            {
                "id": str(self.id),
                "created_at": self.created_at.isoformat(),
                "text": self.text,
            }
        )

    def __repr__(self):
        """Строковое представление модели для отладки.

        Returns:
            str: Строка вида <Message(uuid=..., created_at='...')>.
        """
        return f"<Message(uuid={self.id}, created_at='{self.created_at}')>"
