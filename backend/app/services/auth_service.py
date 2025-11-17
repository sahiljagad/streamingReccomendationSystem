from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.user import User
from app.utils.password_utils import hash_password, verify_password
from datetime import datetime

def register_user(db: Session, email: str, username: str, password: str) -> User:
    #check if email already exists
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    #check if username already exists
    existing_username = db.query(User).filter(User.username == username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    #hash password
    hashed_password = hash_password(password)

    user = User(
        email=email, 
        username=username, 
        password_hash=hashed_password
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user) #refresh the user object to get the id
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User registration failed. Database error occurred",
        )

def authenticate_user(db: Session, email: str, password: str) -> User:
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    
    # If user doesn't exist, return generic error
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"  # Same message as above so as not to leak information
        )
    
    # Update last login timestamp
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Return authenticated user
    return user

def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user