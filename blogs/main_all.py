from fastapi import FastAPI, Depends, status, Response, HTTPException
from .schemas import Blog, Show, User, ShowUser, ShowRealUser
from . import models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import List
# from passlib.context import CryptContext


app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

models.Base.metadata.create_all(bind=engine)

# pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post('/blog', status_code=status.HTTP_201_CREATED, tags = ['blogs'])
def create(request : Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title = request.title, body = request.body, user_id =1)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@app.get('/blog', response_model= List[Show], tags = ['blogs'])
def all(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs

@app.get('/blog/{id}', response_model= Show, tags = ['blogs'])
def read(id:int, response : Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id ==id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='not found')
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return 'not found'
    return blog

@app.delete('/blog/{id}', status_code=status.HTTP_204_NO_CONTENT, tags = ['blogs'])
def delete(id: int, db: Session = Depends(get_db)):
    db.query(models.Blog).filter(models.Blog.id ==id).delete(synchronize_session=False)
    db.commit()
    return 'done'

@app.put('/blog/{id}', status_code=status.HTTP_202_ACCEPTED, tags = ['blogs'])
def update(id:int, request:Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id ==id)
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='not found')
    blog.update(request)
    db.commit()
    return 'updated'

@app.post('/user', response_model=ShowUser, tags = ['users'])
def create_user(request : User, db: Session = Depends(get_db)):
    # hashed_password = pwd_cxt.hash(request.password)
    user = models.User(name = request.name, email = request.email, password = request.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.get('/user/{id}' , response_model=ShowRealUser, tags = ['users'])
def get_user(id:int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='not found')
    return user