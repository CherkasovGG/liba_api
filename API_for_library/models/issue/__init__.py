from sqlalchemy import Column, UUID, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
import uuid
import datetime
from API_for_library.db import Base
from API_for_library.db.mixins import TimestampMixin
from API_for_library.models.books import Books
from API_for_library.models.user import User


class Issue(Base, TimestampMixin):
    __tablename__ = "issued_books"

    id = Column(UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    book_id = Column(UUID, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    issue_date = Column(Date, nullable=False, default=datetime.date.today)
    return_date = Column(Date, nullable=False)
    returned = Column(Boolean, default=False)

    book = relationship("Books", back_populates="issued_books")
    user = relationship("User", back_populates="issued_books")
