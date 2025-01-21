import uuid

from sqlalchemy import Column, String, UUID, Date
from sqlalchemy.orm import relationship

from API_for_library.db import Base
from API_for_library.db.mixins import TimestampMixin


class Authors(Base, TimestampMixin):
    __tablename__ = "authors"

    id = Column(UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String, nullable=False)
    biography = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)

    books = relationship("Books", back_populates="author", cascade="all, delete-orphan")
