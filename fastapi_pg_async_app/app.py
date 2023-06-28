from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI, Depends, HTTPException

from fastapi_pg_async_app import schemas, crud
from fastapi_pg_async_app.config import Settings
from fastapi_pg_async_app.database import DBHolder

app = FastAPI()
settings = Settings()
db_holder = DBHolder(settings)


@app.on_event('startup')
async def app_startup():
    await db_holder.init_models()


@app.get("/users/{user_id}", response_model=schemas.User)
async def get_user(user_id: int, session: AsyncSession = Depends(db_holder.get_session)):
    query = await crud.get_user(session, user_id)
    if query is None:
        raise HTTPException(status_code=404, detail="User not found")
    return query


@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, session: AsyncSession = Depends(db_holder.get_session)):
    new_user = await crud.create_user(session, user)
    return new_user
