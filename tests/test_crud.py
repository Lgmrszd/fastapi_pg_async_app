import pytest
from sqlalchemy import select

from fastapi_pg_async_app import crud, models, schemas, security


@pytest.fixture()
def new_user_schema():
    return schemas.UserCreate(
        username="username",
        password="pass",
        email="email"
    )


@pytest.fixture()
def update_user_schema_1():
    return schemas.UserUpdate(
        username="new_username",
        email="new_email"
    )


@pytest.fixture()
def update_user_schema_2():
    return schemas.UserUpdate(
        password="new_pass"
    )


@pytest.mark.anyio
async def test_user_create(db_session, new_user_schema):
    """
    Create a new user, check that it was created successfully
    """
    user1 = (await db_session.scalars(select(models.User).filter(models.User.id == 1))).first()
    assert user1 is None, "DB should be empty and have no users"
    user_new = await crud.create_user(db_session, new_user_schema)
    assert user_new.id == 1, "First created user should have id of 1"
    assert user_new.username == new_user_schema.username, "Username doesn't match"
    user1 = (await db_session.scalars(select(models.User).filter(models.User.id == 1))).first()
    assert user1 is not None, "DB should return created user"
    assert user1 == user_new, "User object should match"


@pytest.mark.anyio
async def test_user_get(db_session, new_user_schema):
    """
    Get user, verify it's fields
    """
    user1 = await crud.get_user(db_session, 1)
    assert user1.id == 1, "must get same user"
    assert user1.username == new_user_schema.username, "User should keep old username"
    assert user1.email == new_user_schema.email, "User should keep old email"
    assert security.verify_password(new_user_schema.password, user1.hashed_password),\
        "User should keep old password"


@pytest.mark.anyio
async def test_user_update(db_session, new_user_schema, update_user_schema_1, update_user_schema_2):
    """
    First, update only username and email and check that only they have changed. Then, update the password.
    """
    user1 = (await db_session.scalars(select(models.User).filter(models.User.id == 1))).first()
    assert user1.id == 1, "must get same user"
    assert user1.username == new_user_schema.username, "User should keep old username"
    assert user1.email == new_user_schema.email, "User should keep old email"
    user1 = await crud.update_user(db_session, 1, update_user_schema_1)
    assert user1.id == 1, "must get same user"
    assert user1.username == update_user_schema_1.username, "User should get new username"
    assert user1.email == update_user_schema_1.email, "User should get new email"
    assert security.verify_password(new_user_schema.password, user1.hashed_password),\
        "User should keep old password"
    user1 = await crud.update_user(db_session, 1, update_user_schema_2)
    assert user1.id == 1, "must get same user"
    assert security.verify_password(update_user_schema_2.password, user1.hashed_password),\
        "User should get new password"


@pytest.mark.anyio
async def test_used_delete(db_session):
    """
    Delete user and validate
    """
    user1 = (await db_session.scalars(select(models.User).filter(models.User.id == 1))).first()
    assert user1.id == 1, "User should be present before deletion"
    await crud.delete_user(db_session, 1)
    user1 = (await db_session.scalars(select(models.User).filter(models.User.id == 1))).first()
    assert user1 is None, "User should be deleted"
