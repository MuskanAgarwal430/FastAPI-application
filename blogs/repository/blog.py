from .. import models
from ..schemas import Blog
from sqlalchemy.orm import Session
from fastapi import HTTPException, status


def create(request : Blog, db: Session):
    new_blog = models.Blog(title = request.title, body = request.body, user_id =1)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

def get_all(db: Session):
    blogs = db.query(models.Blog).all()
    return blogs

def get(id:int, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id ==id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='not found')
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return 'not found'
    return blog

def delete(id:int, db: Session):
    db.query(models.Blog).filter(models.Blog.id ==id).delete(synchronize_session=False)
    db.commit()
    return 'done'

def update(id:int,request : Blog, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id ==id)
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='not found')
    blog.update(request)
    db.commit()
    return 'updated'

