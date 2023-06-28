import pytest

from fastapi_pg_async_app import crud, schemas, security


@pytest.mark.anyio
async def test_1(scoped_settings):
    print(scoped_settings)
    print(scoped_settings.database_url())


@pytest.mark.anyio
async def test_2(db_session):
    print(db_session)


@pytest.mark.anyio
async def test_3(scoped_settings):
    print(scoped_settings)
    print(scoped_settings.database_url())


@pytest.mark.anyio
async def test_users(db_session):
    user1 = await crud.get_user(db_session, 1)
    assert user1 is None
    user_in = schemas.UserCreate(
        username="username",
        password="pass",
        email="email"
    )
    user_new = await crud.create_user(db_session, user_in)
    print(user_new)
    assert user_new.id == 1
    assert user_new.username == user_in.username
    user1 = await crud.get_user(db_session, 1)
    print(user1, user_new, user1 is user_new, user1 == user_new)
    assert user1 is not None
    assert user1 == user_new


@pytest.mark.anyio
async def test_users_again(db_session):
    user1 = await crud.get_user(db_session, 1)
    assert user1 is not None
    assert user1.username == "username"
    assert security.verify_password("pass", user1.hashed_password)
