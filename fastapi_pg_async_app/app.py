from typing import Annotated, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI, Depends, HTTPException, status

from fastapi_pg_async_app import schemas, crud
from fastapi_pg_async_app.config import Settings
from fastapi_pg_async_app.database import DBHolder

app = FastAPI()
settings = Settings()
db_holder = DBHolder(settings)


SessionDep = Annotated[AsyncSession, Depends(db_holder.get_session)]


@app.on_event('startup')
async def app_startup():
    await db_holder.init_models()


@app.on_event("shutdown")
async def shutdown():
    await db_holder.engine.dispose()


@app.get("/users", response_model=List[schemas.User])
async def get_users(session: SessionDep, skip: int = 0, limit: int = 100):
    """
    Get all users
    """
    query = await crud.get_users(session, skip, limit)
    return query


@app.get("/users/{user_id}", response_model=schemas.User)
async def get_user(user_id: int, session: SessionDep):
    """
    Get user by id, return 404 if not found
    """
    query = await crud.get_user(session, user_id)
    if query is None:
        raise HTTPException(status_code=404, detail="User not found")
    return query


@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, session: SessionDep):
    existing_user = await crud.get_user_by_email(session, user.email) or await crud.get_user_by_username(session, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail=f"{'email' if existing_user.email == user.email else 'username'} "
                                                    f"already in use")
    new_user = await crud.create_user(session, user)
    return new_user


@app.put("/users/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user: schemas.UserUpdate, session: SessionDep):
    existing_user_email = await crud.get_user_by_email(session, user.email)
    existing_user_username = await crud.get_user_by_username(session, user.username)
    if existing_user_email and existing_user_email.id != user_id:
        raise HTTPException(status_code=400, detail="email already in use")
    if existing_user_username and existing_user_username.id != user_id:
        raise HTTPException(status_code=400, detail="username already in use")
    query = await crud.update_user(session, user_id, user)
    if query is None:
        raise HTTPException(status_code=404, detail="User not found")
    return query


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, session: SessionDep):
    result = await crud.delete_user(session, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
