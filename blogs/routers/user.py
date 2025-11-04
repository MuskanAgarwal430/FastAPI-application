from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import ShowUser, ShowRealUser, User
from ..repository import user

router = APIRouter(
    prefix= '/user',
    tags = ['Users']
)

@router.post('/', response_model=ShowUser)
def create_user(request : User, db: Session = Depends(get_db)):
    # hashed_password = pwd_cxt.hash(request.password)
    return user.create_user(request, db)

@router.get('/{id}' , response_model=ShowRealUser)
def get_user(id:int, db: Session = Depends(get_db)):
    return user.get_user(id, db)