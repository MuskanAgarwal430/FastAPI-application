from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .token import verify_token
from . import models, database
from sqlalchemy.orm import Session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # return verify_token(token, credentials_exception)
    token_data = verify_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.email == token_data.email).first()          
    
    if user is None:
        raise credentials_exception
    
    return user