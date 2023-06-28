import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_scoped_session
from testcontainers.postgres import PostgresContainer

from fastapi_pg_async_app.config import Settings, PSQLModel
from fastapi_pg_async_app.database import DBHolder


@pytest.fixture(scope="session")
def event_loop():
    """
    Override event_loop fixture used by pytest_asyncio to set its scope to session
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def scoped_settings():
    """
    Settings fixture with default connection info
    """
    return Settings(
        sqlite=None,
        psql=PSQLModel(
            host="localhost",
            user="user",
            password="pass",
            db="db"
        )
    )


@pytest.fixture(scope='session', autouse=False)
def postgres_instance(scoped_settings: Settings):
    """
    Init new Postgres container and populate settings with correct data
    """
    with PostgresContainer("postgres:14-alpine") as psql:
        scoped_settings.psql.user = psql.POSTGRES_USER
        scoped_settings.psql.password = psql.POSTGRES_PASSWORD
        scoped_settings.psql.db = psql.POSTGRES_DB
        scoped_settings.psql.port = int(psql.get_exposed_port(psql.port_to_expose))
        yield psql


@pytest_asyncio.fixture(scope='session')
async def db_holder(scoped_settings, postgres_instance):
    db_holder_ = DBHolder(scoped_settings)
    await db_holder_.init_models()

    yield db_holder_

    await db_holder_.engine.dispose()


@pytest_asyncio.fixture(scope='session')
async def db_session_factory(db_holder):
    session = async_scoped_session(
        db_holder.async_session,
        scopefunc=asyncio.current_task
    )
    yield session
    await session.close()


@pytest_asyncio.fixture(scope='session')
async def db_session(db_session_factory):
    session_ = db_session_factory()

    yield session_

    try:
        await session_.rollback()
    except Exception:
        pass
