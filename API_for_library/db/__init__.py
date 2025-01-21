import uuid

from sqlalchemy import orm


class Base(orm.DeclarativeBase):
    """Базовая модель"""

    id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
