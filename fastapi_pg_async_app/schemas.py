from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    email: str


class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[str]
    password: Optional[str]


class User(UserBase):
    id: int

    class Config:
        orm_mode = True

