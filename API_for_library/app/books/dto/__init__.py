from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import Optional


class BookCreate(BaseModel):
    title: str
    description: Optional[str] = None
    publication_date: date
    authors: str
    counter: int
    genre: Optional[str] = None
    author_id: UUID

    class Config:
        from_attributes = True


class BookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    publication_date: Optional[date] = None
    authors: Optional[str] = None
    counter: Optional[int] = None
    genre: Optional[str] = None
    author_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class BookResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    publication_date: date
    authors: str
    counter: int
    genre: Optional[str] = None
    author_id: UUID

    class Config:
        from_attributes = True
