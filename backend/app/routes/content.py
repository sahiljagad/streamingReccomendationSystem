from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.services.tmdb_service import (
    search_content,
    get_trending,
    get_or_create_content
)
from app.services.streaming_service import get_content_availability
from app.utils.jwt_utils import get_current_user
from app.models.user import User
from app.services.rating_service import (
    rate_content,
    get_user_ratings,
    get_content_rating,
    delete_rating
)

router = APIRouter()


# Pydantic schemas
class ContentSearchResult(BaseModel):
    id: int
    media_type: str
    title: Optional[str] = None
    name: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    release_date: Optional[str] = None
    first_air_date: Optional[str] = None
    vote_average: Optional[float] = None


class ContentSearchResponse(BaseModel):
    results: list[ContentSearchResult]
    page: int
    total_pages: int
    total_results: int


class ContentDetailResponse(BaseModel):
    id: int
    title: str
    type: str
    release_year: Optional[int] = None
    genres: Optional[list[str]] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    tmdb_rating: Optional[float] = None
    runtime: Optional[int] = None
    director: Optional[str] = None
    cast: Optional[list[str]] = None
    content_rating: Optional[str] = None
    trailer_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class PlatformResponse(BaseModel):
    id: int
    name: str
    display_name: str
    
    class Config:
        from_attributes = True


class AvailabilityResponse(BaseModel):
    content_id: int
    cached: bool
    cache_age_days: Optional[int] = None
    stale: Optional[bool] = None
    platforms: list[PlatformResponse]

class RateContentRequest(BaseModel):
    rating: Optional[int] = None
    status: Optional[str] = None
    watched_on_platform_id: Optional[int] = None
    review_text: Optional[str] = None


class UserContentResponse(BaseModel):
    id: int
    content_id: int
    rating: Optional[int] = None
    status: str
    watched_on_platform_id: Optional[int] = None
    review_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    content: ContentDetailResponse
    
    class Config:
        from_attributes = True


class UserRatingsResponse(BaseModel):
    ratings: list[UserContentResponse]
    total: int
    limit: int
    offset: int

# Routes
@router.get("/search", response_model=ContentSearchResponse)
def search_content_route(
    query: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number")
):
    results = search_content(query, page)
    return results

@router.get("/trending")
def get_trending_content(
    media_type: str = Query("all", regex="^(all|movie|tv)$"),
    time_window: str = Query("week", regex="^(day|week)$")
):
    results = get_trending(media_type, time_window)
    return results

@router.get("/{content_id}", response_model=ContentDetailResponse)
def get_content_details(
    content_id: int,
    media_type: str = Query(..., regex="^(movie|tv)$"),
    db: Session = Depends(get_db)
):
    content = get_or_create_content(db, content_id, media_type)
    return content

@router.get("/{content_id}/availability", response_model=AvailabilityResponse)
def get_content_availability_route(
    content_id: int,
    region: str = Query("US", description="Region code (US, GB, CA, ...)"),
    refresh: bool = Query(False, description="Force refresh even if cached"),
    db: Session = Depends(get_db)
):
   
    result = get_content_availability(
        db, 
        content_id, 
        region, 
        refresh_if_old=not refresh  # If refresh=True, don't use stale cache
    )
    
    return {
        "content_id": content_id,
        "cached": result.get("cached", False),
        "cache_age_days": result.get("cache_age_days"),
        "stale": result.get("stale"),
        "platforms": result.get("platforms", [])
    }

@router.post("/{content_id}/rate", response_model=UserContentResponse)
def rate_content_route(
    content_id: int,
    request: RateContentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user_content = rate_content(
        db=db,
        user_id=current_user.id,
        content_id=content_id,
        rating=request.rating,
        watch_status=request.status,
        watched_on_platform_id=request.watched_on_platform_id,
        review_text=request.review_text
    )
    return user_content


@router.get("/{content_id}/rating", response_model=UserContentResponse)
def get_content_rating_route(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_content = get_content_rating(db, current_user.id, content_id)
    
    if not user_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No rating found for this content"
        )
    
    return user_content


@router.delete("/{content_id}/rating")
def delete_content_rating_route(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return delete_rating(db, current_user.id, content_id)