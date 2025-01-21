from sqlalchemy import Column, String, LargeBinary, Integer
from sqlalchemy.orm import relationship

from API_for_library.db import Base
from API_for_library.db.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(LargeBinary, nullable=False)
    role = Column(String, nullable=False)
    books_count = Column(Integer, nullable=False, default=0)

    issued_books = relationship(
        "Issue", back_populates="user", cascade="all, delete-orphan"
    )
