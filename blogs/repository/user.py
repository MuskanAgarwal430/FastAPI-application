from .. import models
from ..schemas import User
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..hashing import Hash

def create_user(request : User, db: Session):
    print("Password value:", request.password)
    user = models.User(name = request.name, email = request.email, password = Hash.bcrypt(request.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(id:int, db: Session):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='not found')
    return user