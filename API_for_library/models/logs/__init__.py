from sqlalchemy import Column, UUID, String, Date, Text
from sqlalchemy.orm import relationship
import uuid
import datetime
from API_for_library.db import Base
from API_for_library.db.mixins import TimestampMixin


class Logs(Base, TimestampMixin):
    __tablename__ = "logs"

    id = Column(UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    event_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    timestamp = Column(Date, default=datetime.datetime.now(), nullable=False)
