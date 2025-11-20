import requests
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from starlette.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE,
)
from app.config import settings
from app.models.content import Content

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


def search_content(query: str, page: int = 1) -> dict:
    if not settings.TMDB_API_KEY:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="TMDB API key not configured",
        )

    url = f"{TMDB_BASE_URL}/search/multi"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "query": query,
        "page": page,
        "include_adult": False,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # filter only movies and tv shows
        results = [
            item
            for item in data.get("results", [])
            if item.get("media_type") in ["movie", "tv"]
        ]

        return {
            "results": results,
            "page": data.get("page", 1),
            "total_pages": data.get("total_pages", 1),
            "total_results": len(results),
        }

    except requests.RequestException as e:
        raise HTTPException(
            status_code=HTTP_503_SERVICE_UNAVAILABLE, detail=f"TMDB API error: {str(e)}"
        )


def get_movie_details(movie_id: int):
    if not settings.TMDB_API_KEY:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="TMDB API key not configured",
        )

    url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "append_to_response": "credits,videos",  # Get cast and trailers too
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"TMDB API error: {str(e)}",
        )


def get_tv_details(tv_id: int) -> dict:
    if not settings.TMDB_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="TMDB API key not configured",
        )

    url = f"{TMDB_BASE_URL}/tv/{tv_id}"
    params = {"api_key": settings.TMDB_API_KEY, "append_to_response": "credits,videos"}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"TMDB API error: {str(e)}",
        )


def get_or_create_content(db: Session, tmdb_id: int, media_type: str) -> Content:
    #check if content already exists in DB
    content = db.query(Content).filter(Content.id == tmdb_id).first()

    if content:
        return content

    if media_type == "movie":
        tmdb_data = get_movie_details(tmdb_id)
    elif media_type == "tv":
        tmdb_data = get_tv_details(tmdb_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid media type"
        )

    if media_type == "movie":
        title = tmdb_data.get("title")
        release_year = tmdb_data.get("release_date", "")[:4] if tmdb_data.get("release_date") else None
        runtime = tmdb_data.get("runtime")
    else:
        title = tmdb_data.get("name")
        release_year = tmdb_data.get("first_air_date", "")[:4] if tmdb_data.get("first_air_date") else None
        episode_runtimes = tmdb_data.get("episode_run_time", [])
        runtime = episode_runtimes[0] if episode_runtimes else None

    genres = [genre["name"] for genre in tmdb_data.get("genres", [])]
    cast = [actor["name"] for actor in tmdb_data.get("credits", {}).get("cast", [])[:5]]

    director = None
    if media_type == "movie":
        crew = tmdb_data.get("credits", {}).get("crew", [])
        for person in crew:
            if person.get("job") == "Director":
                director = person.get("name")
                break

    trailer_url = None
    videos = tmdb_data.get("videos", {}).get("results", [])
    for video in videos:
        if video.get("type") == "Trailer" and video.get("site") == "YouTube":
            trailer_url = f"https://www.youtube.com/watch?v={video.get('key')}"
            break

    content = Content(
        id=tmdb_id,
        title=title,
        type=media_type,
        release_year=int(release_year) if release_year and release_year.isdigit() else None,
        genres=genres,
        overview=tmdb_data.get("overview"),
        poster_path=tmdb_data.get("poster_path"),
        backdrop_path=tmdb_data.get("backdrop_path"),
        tmdb_rating=tmdb_data.get("vote_average"),
        runtime=runtime,
        director=director,
        cast=cast,
        trailer_url=trailer_url
    )
    
    db.add(content)
    db.commit()
    db.refresh(content)
    
    return content

def get_trending(media_type: str = "all", time_window: str = "week") -> dict:
    if not settings.TMDB_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="TMDB API key not configured"
        )
    
    url = f"{TMDB_BASE_URL}/trending/{media_type}/{time_window}"
    params = {
        "api_key": settings.TMDB_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"TMDB API error: {str(e)}"
        )

    
