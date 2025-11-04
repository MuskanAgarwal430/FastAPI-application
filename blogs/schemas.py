from pydantic import BaseModel
from typing import List

class Blog(BaseModel):
    title: str
    body: str
    

class Bloger(Blog):
    class Config():
        orm_mode = True

class User(BaseModel):
    name: str
    email: str
    password: str

class ShowUser(BaseModel): #user
    name: str
    email: str
    # blogs: List[Bloger] = []
    class Config():
        orm_mode = True

class ShowRealUser(ShowUser): #user #main
    blogs: List[Bloger] = []
    class Config():
        orm_mode = True


class Show(BaseModel): #blog #main
    title: str
    body: str
    creator : ShowUser
    class Config():
        orm_mode = True


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None