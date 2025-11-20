from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.services.tmdb_service import (
    search_content,
    get_trending,
    get_or_create_content
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