import datetime
from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from .dto import BookResponse, BookCreate, BookUpdate

from API_for_library.db.session import get_session
from API_for_library.db.repository import DatabaseRepository
from API_for_library.models.books import Books
from ..user import check_admin
from ..author import check_user
from API_for_library.models.user import User
from API_for_library.models.logs import Logs

books_router = APIRouter(prefix="/books", tags=["books"])


def get_books_repository(
    session: AsyncSession = Depends(get_session),
) -> DatabaseRepository[Books]:
    return DatabaseRepository(model=Books, session=session)


def get_log_repository(
    session: AsyncSession = Depends(get_session),
) -> DatabaseRepository[Logs]:
    return DatabaseRepository(model=Logs, session=session)


@books_router.post(
    "/",
    response_model=BookResponse,
    responses={
        status.HTTP_201_CREATED: {"description": "Book created successfully."},
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid input data or foreign key violation."
        },
    },
)
async def create_book(
    book: BookCreate,
    repository: DatabaseRepository[Books] = Depends(get_books_repository),
    logs_repo: DatabaseRepository[Logs] = Depends(get_log_repository),
    user: User = Depends(check_admin),
):
    """Создать новую книгу"""
    try:
        book = await repository.create(book.dict())
        await logs_repo.create(
            {
                "event_type": "CREATE",
                "description": f"User {user.id} added new book {book.title} which have id {book.id}",
                "timestamp": datetime.datetime.now(),
            }
        )
        return book
    except IntegrityError as e:
        if "foreign key constraint" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Author with the provided ID does not exist",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Integrity error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating book: {str(e)}",
        )


@books_router.get(
    "/{book_id}",
    response_model=BookResponse,
    responses={
        status.HTTP_200_OK: {"description": "Book retrieved successfully."},
        status.HTTP_404_NOT_FOUND: {"description": "Book not found."},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid book ID."},
    },
)
async def get_book(
    book_id: UUID,
    repository: DatabaseRepository[Books] = Depends(get_books_repository),
    user: User = Depends(check_user),
):
    """Получить книгу по ID"""
    try:
        book = await repository.get(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found."
            )
        return book
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for book_id.",
        )


@books_router.put(
    "/{book_id}",
    response_model=BookResponse,
    responses={
        status.HTTP_200_OK: {"description": "Book updated successfully."},
        status.HTTP_404_NOT_FOUND: {"description": "Book not found."},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid input data or book ID."},
    },
)
async def update_book(
    book_id: UUID,
    data: BookUpdate,
    repository: DatabaseRepository[Books] = Depends(get_books_repository),
    logs_repo: DatabaseRepository[Logs] = Depends(get_log_repository),
    user: User = Depends(check_admin),
):
    """Обновить информацию о книге"""
    try:
        updated_book = await repository.update(book_id, data.dict())
        if not updated_book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found."
            )
        await logs_repo.create(
            {
                "event_type": "UPDATE",
                "description": f"User {user.id} update book {updated_book.title} which have id {updated_book.id}",
                "timestamp": datetime.datetime.now(),
            }
        )
        return updated_book
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for book_id.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating book: {str(e)}",
        )


@books_router.delete(
    "/{book_id}",
    responses={
        status.HTTP_200_OK: {"description": "Book deleted successfully."},
        status.HTTP_404_NOT_FOUND: {"description": "Book not found."},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid book ID."},
    },
)
async def delete_book(
    book_id: UUID,
    repository: DatabaseRepository[Books] = Depends(get_books_repository),
    logs_repo: DatabaseRepository[Logs] = Depends(get_log_repository),
    user: User = Depends(check_admin),
):
    """Удалить книгу"""
    try:
        await repository.delete(book_id)
        await logs_repo.create(
            {
                "event_type": "CREATE",
                "description": f"User {user.id} delete book {book_id}",
                "timestamp": datetime.datetime.now(),
            }
        )
        return {"message": "Book deleted successfully"}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for book_id.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting book: {str(e)}",
        )


@books_router.get(
    "/",
    responses={
        status.HTTP_200_OK: {"description": "Books retrieved successfully."},
        status.HTTP_400_BAD_REQUEST: {"description": "Error retrieving books."},
    },
)
async def list_books(
    repository: DatabaseRepository[Books] = Depends(get_books_repository),
    user: User = Depends(check_user),
):
    """Получить список всех книг"""
    try:
        return await repository.all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving books: {str(e)}",
        )
