from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List
from ..schemas import Show, Blog, User
from ..repository import blog
from ..oauth2 import get_current_user

# get_db = database.get_db()

router = APIRouter(
    prefix= '/blog',
    tags = ['Blogs']
)

@router.post('/', status_code=status.HTTP_201_CREATED)
def create(request : Blog, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    return blog.create(request, db)

@router.get('/', response_model= List[Show])
def all(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    return blog.get_all(db)

@router.get('/{id}', response_model= Show)
def read(id:int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    return blog.get(id, db)

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT,)
def delete(id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    return blog.delete(id, db)

@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id:int, request:Blog, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    return blog.update(id, request, db)