from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.utils.jwt_utils import get_current_user
from app.models.user import User
from app.services.user_service import (
    get_user_platforms,
    update_user_platforms,
    get_all_platforms
)

router = APIRouter()


# Pydantic schemas
class PlatformResponse(BaseModel):
    id: int
    name: str
    display_name: str
    logo_url: str | None
    website_url: str | None
    
    class Config:
        from_attributes = True


class UserPlatformsResponse(BaseModel):
    platforms: list[PlatformResponse]


class UpdatePlatformsRequest(BaseModel):
    platform_ids: list[int]

@router.get("/platforms", response_model=UserPlatformsResponse)
def get_user_platforms_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    platforms = get_user_platforms(db, current_user.id)
    return {"platforms": platforms}


@router.put("/platforms", response_model=UserPlatformsResponse)
def update_user_platforms_route(
    request: UpdatePlatformsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    platforms = update_user_platforms(db, current_user.id, request.platform_ids)
    return {"platforms": platforms}

@router.get("/platforms/available", response_model=UserPlatformsResponse)
def get_available_platforms(db: Session = Depends(get_db)):
    platforms = get_all_platforms(db)
    return {"platforms": platforms}