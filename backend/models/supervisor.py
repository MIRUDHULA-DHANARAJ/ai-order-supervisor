from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Supervisor(Base):
    __tablename__ = "supervisors"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    base_instruction: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    available_actions: Mapped[list] = mapped_column(
        JSON,
        nullable=False
    )

    wake_policy: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="balanced"
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="llama-3.3-70b-versatile"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    runs = relationship(
        "Run",
        back_populates="supervisor"
    )