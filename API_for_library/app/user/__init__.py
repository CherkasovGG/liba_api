import datetime
import random

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..auth.generate_token import JWTService
from ..auth.generate_password import hash_password
from ..user.dto import UserCreateDTO, UserResponseDTO
from API_for_library.models.user import User
from API_for_library.models.logs import Logs
from API_for_library.db.repository import DatabaseRepository
from API_for_library.db.session import get_session

user_router = APIRouter(prefix="/user", tags=["user"])

jwt_service = JWTService()
http_bearer_scheme = HTTPBearer()


def get_log_repository(
    session: AsyncSession = Depends(get_session),
) -> DatabaseRepository[Logs]:
    return DatabaseRepository(model=Logs, session=session)


fun_verb = [
    "juggle",
    "dance",
    "fart",
    "yodel",
    "twerk",
    "snore",
    "giggle",
    "prance",
    "jive",
    "wiggle",
    "sneeze",
    "slurp",
    "guffaw",
    "sashay",
    "twirl",
    "bounce",
    "mimic",
    "scoot",
    "flap",
    "shuffle",
]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer_scheme),
    session: AsyncSession = Depends(get_session),
):
    """Получение текущего пользователя из токена"""
    token = credentials.credentials
    try:
        payload = jwt_service.decode_jwt(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing 'sub'.",
            )
        user_repo = DatabaseRepository(User, session)
        user = await user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token. Error: {str(e)}",
        )


async def check_admin(current_user: User = Depends(get_current_user)):
    """Проверка, является ли пользователь администратором"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return current_user


@user_router.get(
    "/all",
    response_model=List[UserResponseDTO],
    responses={
        status.HTTP_200_OK: {"description": "List of all users."},
        status.HTTP_403_FORBIDDEN: {"description": "Access denied."},
    },
)
async def get_all_users(
    admin_user: User = Depends(check_admin),
    session: AsyncSession = Depends(get_session),
    logs_repo: DatabaseRepository[Logs] = Depends(get_log_repository),
):
    """Возвращает список всех зарегистрированных читателей (только для администраторов)."""
    user_repo = DatabaseRepository(User, session)
    all_users = await user_repo.filter(User.role != "admin")
    await logs_repo.create(
        {
            "event_type": "GET ALL USER",
            "description": f"User {admin_user.id} wanna see all users",
            "timestamp": datetime.datetime.now(),
        }
    )
    return [UserResponseDTO.from_orm(user) for user in all_users]


@user_router.post(
    "/",
    response_model=UserResponseDTO,
    responses={
        status.HTTP_201_CREATED: {"description": "User created successfully."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Bad request. Invalid input data."
        },
        status.HTTP_409_CONFLICT: {"description": "Conflict. User already exists."},
    },
)
async def create_user_route(
    user_data: UserCreateDTO,
    session: AsyncSession = Depends(get_session),
    logs_repo: DatabaseRepository[Logs] = Depends(get_log_repository),
):
    """Создает юзера по переданным данным"""
    user_repo = DatabaseRepository(User, session)
    existing_user = await user_repo.filter(User.email == user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    hashed_password = hash_password(user_data.password)
    user_data_dict = user_data.dict()
    user_data_dict["password_hash"] = hashed_password
    del user_data_dict["password"]

    created_user = await user_repo.create(user_data_dict)
    verb = fun_verb[random.randint(0, 19)]
    await logs_repo.create(
        {
            "event_type": "NEW USER",
            "description": f"User {created_user.id} has been selected to {verb}",
            "timestamp": datetime.datetime.now(),
        }
    )
    return UserResponseDTO.from_orm(created_user)


@user_router.patch(
    "/",
    response_model=UserResponseDTO,
    responses={
        status.HTTP_200_OK: {"description": "User patched successfully."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Bad request. Invalid input data."
        },
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
)
async def patch_user_data(
    user_data: UserCreateDTO,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Частично редактирует данные юзера."""
    user_repo = DatabaseRepository(User, session)
    updated_user = await user_repo.update(
        current_user.id, user_data.dict(exclude_unset=True)
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return UserResponseDTO.from_orm(updated_user)


@user_router.put(
    "/",
    response_model=UserResponseDTO,
    responses={
        status.HTTP_200_OK: {"description": "User updated successfully."},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
)
async def update_user_data(
    user_data: UserCreateDTO,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Редактирует данные юзера."""
    user_repo = DatabaseRepository(User, session)
    updated_user = await user_repo.update(current_user.id, user_data.dict())
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return UserResponseDTO.from_orm(updated_user)


@user_router.delete(
    "/",
    responses={
        status.HTTP_200_OK: {"description": "User deleted successfully."},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
)
async def delete_user(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Удаляет юзера."""
    user_repo = DatabaseRepository(User, session)
    await user_repo.delete(current_user.id)
    return {"message": "User deleted successfully."}


@user_router.get(
    "/",
    response_model=UserResponseDTO,
    responses={
        status.HTTP_200_OK: {"description": "User data retrieved successfully."},
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized. Invalid or missing JWT token."
        },
        status.HTTP_404_NOT_FOUND: {"description": "User not found."},
    },
)
async def get_user_route(current_user: User = Depends(get_current_user)):
    """Выдает данные юзера по jwt токену."""
    return UserResponseDTO.from_orm(current_user)
