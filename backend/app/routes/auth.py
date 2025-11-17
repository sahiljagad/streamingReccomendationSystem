from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.database import get_db
from app.services.auth_service import register_user, authenticate_user
from app.utils.jwt_utils import create_access_token, get_current_user
from app.models.user import User

router = APIRouter()

# Schema for registration request
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


# Schema for login request
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Schema for token response
class Token(BaseModel):
    access_token: str
    token_type: str


# Schema for user info response
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    last_login: datetime | None
    
    class Config:
        from_attributes = True


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    
    # create user in DB
    user = register_user(
        db=db,
        email=user_data.email,
        username=user_data.username,
        password=user_data.password
    )

    # create JWT token
    access_token = create_access_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):

    #Verify credentials
    user = authenticate_user(
        db=db,
        email=user_data.email,
        password=user_data.password
    )
    
    # Create JWT token
    access_token = create_access_token(data={"sub": user.id})
    
    # Return token
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user
