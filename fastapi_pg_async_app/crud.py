from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pg_async_app import models, schemas, security


async def get_user(session: AsyncSession, user_id: int) -> models.User | None:
    result = await session.scalars(select(models.User).filter(models.User.id == user_id))
    user = result.first()
    return user


async def create_user(session: AsyncSession, user_in: schemas.UserCreate) -> models.User:
    new_user = models.User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=security.hash_password(user_in.password)
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def delete_user(session: AsyncSession, user_id: int) -> bool:
    result = await session.scalars(select(models.User).filter(models.User.id == user_id))
    user = result.first()
    if not user:
        return False
    await session.delete(user)
    await session.commit()
    return True
