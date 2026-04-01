from jose import jwt, JWTError
from datetime import datetime, timedelta
from config import settings
from fastapi import HTTPException, status

SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRATION_TIME = settings.ACCESS_TOKEN_EXPIRATION_TIME
ALGORITHM = settings.ALGORITHM

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes= ACCESS_TOKEN_EXPIRATION_TIME)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") 
