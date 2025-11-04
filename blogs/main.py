from fastapi import FastAPI
from . import models
from .database import engine
from .routers import blog, user, authentication
# from passlib.context import CryptContext


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(authentication.router)
app.include_router(blog.router)
app.include_router(user.router)

# pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

