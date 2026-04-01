from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from auth_utils import hash_password, verify_password
from schemas.schemas import UserCreate, UserResponse
from models.models import User
from sqlalchemy import select 
from token_utils import create_access_token, verify_access_token

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid Token")
    
    result = await db.execute(select(User).where(int(user_id )== User.uid))
    existing_user = result.scalar_one_or_none()
    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return existing_user

@router.post("/register", response_model=UserResponse)
async def register_user(cred: UserCreate, db: AsyncSession = Depends(get_db)):
    response = await db.execute(select(User).where(User.email == cred.email))
    existing_user = response.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pwd = hash_password(cred.pwd)
    new_user = User(
        email = cred.email,
        username = cred.username,
        hashed_pwd = hashed_pwd
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    response = await db.execute(select(User).where(User.email == form_data.username))
    existing_user = response.scalar_one_or_none()
    if not existing_user or not verify_password(form_data.password, existing_user.hashed_pwd):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": str(existing_user.uid)})
    return {"access_token": token, "token_type": "bearer"}


@router.delete("/delete")
async def delete_user(uid: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    response = await db.execute(select(User).where(uid == current_user.uid))
    existing_user = response.scalar_one_or_none()

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(existing_user)
    await db.commit()

    return {"id":uid, "detail": "user deleted successfully"}