from fastapi import APIRouter, HTTPException, Depends, status
from uuid import UUID
from datetime import timedelta
import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from API_for_library.models.issue import Issue
from API_for_library.models.books import Books
from API_for_library.models.user import User
from API_for_library.models.logs import Logs
from API_for_library.db.repository import DatabaseRepository
from API_for_library.db.session import get_session
from ..books import get_books_repository
from ..author import check_user

issue_router = APIRouter(prefix="/issues", tags=["issues"])


def get_issue_repository(
    session: AsyncSession = Depends(get_session),
) -> DatabaseRepository[Issue]:
    return DatabaseRepository(model=Issue, session=session)


def get_log_repository(
    session: AsyncSession = Depends(get_session),
) -> DatabaseRepository[Logs]:
    return DatabaseRepository(model=Logs, session=session)


@issue_router.post(
    "/{book_id}",
    responses={
        status.HTTP_201_CREATED: {"description": "Book issued successfully."},
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid input data or foreign key violation."
        },
    },
)
async def issue_book(
    book_id: UUID,
    user_id: UUID,
    issue_repo: DatabaseRepository[Issue] = Depends(get_issue_repository),
    book_repo: DatabaseRepository[Books] = Depends(get_books_repository),
    logs_repo: DatabaseRepository[Logs] = Depends(get_log_repository),
    user: User = Depends(check_user),
    db: AsyncSession = Depends(get_session),
    days: int = 14,
):
    """Выдать книгу пользователю"""
    try:
        user_repo = DatabaseRepository(User, db)
        user = await user_repo.filter(User.id == user_id)

        if not user[0]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        issued_books = user[0].books_count
        if issued_books >= 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has already issued 5 books",
            )

        book = await book_repo.get(book_id)
        if not book or book.counter <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Book is not available"
            )

        issue_date = datetime.date.today()
        return_date = issue_date + timedelta(days=days)

        issue_data = {
            "book_id": book_id,
            "user_id": user_id,
            "issue_date": issue_date,
            "return_date": return_date,
            "returned": False,
        }

        book.counter -= 1
        issued_books += 1
        await book_repo.update(book.id, {"counter": book.counter})
        await user_repo.update(user[0].id, {"books_count": issued_books})

        await logs_repo.create(
            {
                "event_type": "ISSUE",
                "description": f"Book {book_id} issued to user {user_id}",
                "timestamp": datetime.datetime.now(),
            }
        )

        return await issue_repo.create(issue_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving books: {str(e)}",
        )


@issue_router.post(
    "/return/{issue_id}",
    responses={
        status.HTTP_200_OK: {"description": "Book returned successfully."},
        status.HTTP_404_NOT_FOUND: {"description": "Issue not found."},
    },
)
async def return_book(
    issue_id: UUID,
    db: AsyncSession = Depends(get_session),
    issue_repo: DatabaseRepository[Issue] = Depends(get_issue_repository),
    book_repo: DatabaseRepository[Books] = Depends(get_books_repository),
    logs_repo: DatabaseRepository[Logs] = Depends(get_log_repository),
    user: User = Depends(check_user),
):
    """Обработчик для возврата книги пользователем"""
    try:
        issue: Issue = await issue_repo.get(issue_id)
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found"
            )

        if issue.returned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book is already returned",
            )

        book: Books = await book_repo.get(issue.book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )

        book.counter += 1
        await book_repo.update(book.id, {"counter": book.counter})
        await issue_repo.update(issue.id, {"returned": True})

        user_repo = DatabaseRepository(User, db)
        user = await user_repo.filter(User.id == issue.user_id)
        if not user[0]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        await user_repo.update(user[0].id, {"books_count": user[0].books_count - 1})

        await logs_repo.create(
            {
                "event_type": "RETURN",
                "description": f"Book {issue.book_id} returned by user {issue.user_id}",
                "timestamp": datetime.datetime.now(),
            }
        )

        return {"message": "Book returned successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving books: {str(e)}",
        )
