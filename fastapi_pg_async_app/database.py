from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker

from fastapi_pg_async_app.config import Settings

Base = declarative_base()


class DBHolder:
    engine: AsyncEngine

    def __init__(self, settings: Settings):
        self.engine = create_async_engine(settings.database_url(), echo=False)
        self.async_session = async_sessionmaker(
            self.engine, expire_on_commit=False
        )

    async def init_models(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_models(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def get_session(self) -> AsyncSession:
        session: AsyncSession
        async with self.async_session() as session:
            try:
                yield session
            finally:
                await session.close()
