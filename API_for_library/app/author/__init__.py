import datetime

from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from sqlalchemy.orm import joinedload

from API_for_library.db.session import get_session
from API_for_library.db.repository import DatabaseRepository
from API_for_library.models.authors import Authors
from .dto import AuthorCreate, AuthorResponse, AuthorUpdate
from ..user import check_admin, get_current_user
from API_for_library.models.user import User
from API_for_library.models.logs import Logs

author_router = APIRouter(prefix="/author", tags=["author"])


def get_authors_repository(
    session: AsyncSession = Depends(get_session),
) -> DatabaseRepository[Authors]:
    return DatabaseRepository(Authors, session)


def get_log_repository(
    session: AsyncSession = Depends(get_session),
) -> DatabaseRepository[Logs]:
    return DatabaseRepository(model=Logs, session=session)


async def check_user(current_user: User = Depends(get_current_user)):
    """Проверка, является ли пользователь зарегистрированным"""
    if current_user.role != "admin" and current_user.role != "reader":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return current_user


@author_router.post(
    "/",
    response_model=AuthorResponse,
)
async def create_author(
    data: AuthorCreate,
    repository: DatabaseRepository[Authors] = Depends(get_authors_repository),
    logs_repo: DatabaseRepository[Logs] = Depends(get_log_repository),
    user: User = Depends(check_admin),
):
    """Создать нового автора"""
    new_author = await repository.create(data.dict())

    async with get_session() as session:
        result = await session.execute(
            select(Authors)
            .options(joinedload(Authors.books))
            .filter(Authors.id == new_author.id)
        )
        author_with_books = result.scalars().first()

    await logs_repo.create(
        {
            "event_type": "CREATE",
            "description": f"User {user.id} added new author {new_author.name} who have id {new_author.id}",
            "timestamp": datetime.datetime.now(),
        }
    )

    return author_with_books


@author_router.get(
    "/author_id",
    response_model=AuthorResponse,
    responses={
        status.HTTP_200_OK: {"description": "Author retrieved successfully."},
        status.HTTP_404_NOT_FOUND: {"description": "Author not found."},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid author ID."},
    },
)
async def get_author(
    author_id: UUID,
    repository: DatabaseRepository[Authors] = Depends(get_authors_repository),
    user: User = Depends(check_user),
):
    """Получить автора по ID"""
    try:
        author = await repository.get(author_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Author not found."
            )
        return author
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for author_id.",
        )


@author_router.patch(
    "/author_id",
    response_model=AuthorResponse,
    responses={
        status.HTTP_200_OK: {"description": "Author updated successfully."},
        status.HTTP_404_NOT_FOUND: {"description": "Author not found."},
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid input data or author ID."
        },
    },
)
async def update_author(
    author_id: UUID,
    data: AuthorUpdate,
    repository: DatabaseRepository[Authors] = Depends(get_authors_repository),
    logs_repo: DatabaseRepository[Logs] = Depends(get_log_repository),
    user: User = Depends(check_admin),
):
    """Обновить информацию об авторе"""
    try:
        updated_author = await repository.update(author_id, data.dict())
        if not updated_author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Author not found."
            )
        await logs_repo.create(
            {
                "event_type": "UPDATE",
                "description": f"User {user.id} update info for author {updated_author.name} who have id {updated_author.id}",
                "timestamp": datetime.datetime.now(),
            }
        )
        return updated_author
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for author_id.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating author: {str(e)}",
        )


@author_router.delete(
    "/{author_id}",
    responses={
        status.HTTP_200_OK: {"description": "Author deleted successfully."},
        status.HTTP_404_NOT_FOUND: {"description": "Author not found."},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid author ID."},
    },
)
async def delete_author(
    author_id: UUID,
    repository: DatabaseRepository[Authors] = Depends(get_authors_repository),
    logs_repo: DatabaseRepository[Logs] = Depends(get_log_repository),
    user: User = Depends(check_admin),
):
    """Удалить автора"""
    try:
        await repository.delete(author_id)
        await logs_repo.create(
            {
                "event_type": "DELETE",
                "description": f"User {user.id} delete author {author_id}",
                "timestamp": datetime.datetime.now(),
            }
        )
        return {
            "content": {"message": "Author deleted successfully"},
            "status_code": status.HTTP_200_OK,
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for author_id.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting author: {str(e)}",
        )
