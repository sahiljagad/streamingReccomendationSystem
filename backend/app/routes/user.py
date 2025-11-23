from typing import Optional
from fastapi import APIRouter, Depends, Query
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
from app.services.rating_service import get_user_ratings as get_ratings_service
from datetime import datetime

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

class ContentBasicInfo(BaseModel):
    id: int
    title: str
    type: str
    poster_path: Optional[str] = None
    release_year: Optional[int] = None
    
    class Config:
        from_attributes = True


class UserContentItem(BaseModel):
    id: int
    content_id: int
    rating: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime
    content: ContentBasicInfo
    
    class Config:
        from_attributes = True


class UserRatingsListResponse(BaseModel):
    ratings: list[UserContentItem]
    total: int
    limit: int
    offset: int

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

@router.get("/ratings", response_model=UserRatingsListResponse)
def get_user_ratings_route(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = get_ratings_service(
        db=db,
        user_id=current_user.id,
        status_filter=status,
        limit=limit,
        offset=offset
    )
    return result