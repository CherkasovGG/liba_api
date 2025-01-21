import uuid
from typing import Generic, TypeVar, Optional, List

from sqlalchemy import BinaryExpression, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import exc
from sqlalchemy.orm import sessionmaker

from . import Base
from .session import engine

Model = TypeVar("Model", bound=Base)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class DatabaseRepository(Generic[Model]):

    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def create(self, data: dict) -> Model:
        """Создание новой записи"""
        try:
            async with SessionLocal() as session:
                instance = self.model(**data)
                session.add(instance)
                await session.commit()
                await session.refresh(instance)
                return instance
        except IntegrityError as e:
            await session.rollback()
            raise ValueError(f"Ошибка при создании записи: {e}")

    async def get(self, pk: uuid.UUID) -> Optional[Model]:
        """Получение записи по pk"""
        async with SessionLocal() as session:
            query = select(self.model).filter(self.model.id == pk)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def filter(self, *expressions: BinaryExpression) -> List[Model]:
        """Фильтрация записей по условию"""
        async with SessionLocal() as session:
            query = select(self.model).filter(*expressions)
            result = await session.execute(query)
            return result.scalars().all()

    async def update(self, pk: uuid.UUID, data: dict) -> Optional[Model]:
        """Обновление записи"""
        try:
            async with SessionLocal() as session:
                query = (
                    update(self.model)
                    .where(self.model.id == pk)
                    .values(**data)
                    .execution_options(synchronize_session="fetch")
                )
                await session.execute(query)
                await session.commit()
                return await self.get(pk)
        except exc.UnmappedInstanceError as e:
            await session.rollback()
            raise ValueError(f"Ошибка при обновлении записи: {e}")

    async def delete(self, pk: uuid.UUID) -> None:
        """Удаление записи"""
        try:
            async with SessionLocal() as session:
                query = delete(self.model).where(self.model.id == pk)
                await session.execute(query)
                await session.commit()
        except exc.UnmappedInstanceError as e:
            await session.rollback()
            raise ValueError(f"Ошибка при удалении записи: {e}")

    async def all(self) -> List[Model]:
        """Получение всех записей из таблицы"""
        try:
            async with SessionLocal() as session:
                query = select(self.model)
                result = await session.execute(query)
                return result.scalars().all()
        except Exception as e:
            raise ValueError(f"Ошибка при получении записей: {e}")
