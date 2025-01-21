from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import Optional


class AuthorCreate(BaseModel):
    name: str
    biography: str
    birth_date: date

    class Config:
        from_attributes = True


class AuthorUpdate(BaseModel):
    name: Optional[str] = None
    biography: Optional[str] = None
    birth_date: Optional[date] = None

    class Config:
        from_attributes = True


class AuthorResponse(BaseModel):
    id: UUID
    name: str
    biography: str
    birth_date: date

    class Config:
        from_attributes = True
