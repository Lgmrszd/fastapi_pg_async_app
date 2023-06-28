from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pg_async_app import models, schemas, security


async def get_users(session: AsyncSession, skip: int = 0, limit: int = 100):
    if limit > 100:
        limit = 100
    result = await session.scalars(select(models.User).offset(skip).limit(limit))
    return result.all()


async def get_user(session: AsyncSession, user_id: int) -> models.User | None:
    result = await session.scalars(select(models.User).filter(models.User.id == user_id))
    user = result.first()
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> models.User | None:
    result = await session.scalars(select(models.User).filter(models.User.email == email))
    user = result.first()
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> models.User | None:
    result = await session.scalars(select(models.User).filter(models.User.username == username))
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


async def update_user(session: AsyncSession, user_id: int, user: schemas.UserUpdate):
    db_user: models.User
    result = await session.scalars(select(models.User).filter(models.User.id == user_id))
    db_user = result.first()
    if not db_user:
        return None
    if user.username:
        db_user.username = user.username
    if user.email:
        db_user.email = user.email
    if user.password:
        db_user.hashed_password = security.hash_password(user.password)
    session.add(db_user)
    await session.commit()
    return db_user


async def delete_user(session: AsyncSession, user_id: int) -> bool:
    result = await session.scalars(select(models.User).filter(models.User.id == user_id))
    user = result.first()
    if not user:
        return False
    await session.delete(user)
    await session.commit()
    return True
