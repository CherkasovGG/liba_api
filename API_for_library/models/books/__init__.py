import uuid

from sqlalchemy import Column, String, UUID, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from API_for_library.db import Base
from API_for_library.db.mixins import TimestampMixin
from API_for_library.models.authors import Authors


class Books(Base, TimestampMixin):
    __tablename__ = "books"

    id = Column(UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    publication_date = Column(Date, nullable=False, default=datetime.now)
    authors = Column(String, nullable=False)
    counter = Column(Integer, nullable=False)
    genre = Column(String, nullable=True)
    author_id = Column(
        UUID, ForeignKey("authors.id", ondelete="CASCADE"), nullable=False
    )

    author = relationship("Authors", back_populates="books")
    issued_books = relationship(
        "Issue", back_populates="book", cascade="all, delete-orphan"
    )
