from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.streaming_availability import StreamingAvailability
from app.models.platform import Platform
from app.models.content import Content
from app.services.tmdb_service import get_watch_providers


def update_content_availability(db: Session, content_id: int, media_type: str, region: str = "US"):
    
    # Get watch providers from TMDB
    provider_data = get_watch_providers(content_id, media_type, region)
    tmdb_providers = provider_data.get("providers", [])
    
    # Get platforms with their TMDB provider IDs
    platforms = db.query(Platform).filter(Platform.tmdb_provider_id.isnot(None)).all()
    platform_map = {p.tmdb_provider_id: p.id for p in platforms}
    
    # Delete old availability data for content
    db.query(StreamingAvailability).filter(
        StreamingAvailability.content_id == content_id,
        StreamingAvailability.region == region
    ).delete()
    
    # Add new availability data
    available_platform_ids = []
    
    if tmdb_providers:
        # Content is available on some platforms
        for provider in tmdb_providers:
            tmdb_provider_id = provider.get("provider_id")
            
            # Check if this provider is one we track
            if tmdb_provider_id in platform_map:
                platform_id = platform_map[tmdb_provider_id]
                availability = StreamingAvailability(
                    content_id=content_id,
                    platform_id=platform_id,
                    region=region,
                    last_checked=datetime.utcnow()
                )
                db.add(availability)
                available_platform_ids.append(platform_id)
    
    # create entry to mark content checked
    if not available_platform_ids:
        # No platforms available
        availability = StreamingAvailability(
            content_id=content_id,
            platform_id=None,  # not available on any tracked platform
            region=region,
            last_checked=datetime.utcnow()
        )
        db.add(availability)
    
    db.commit()
    
    return available_platform_ids


def get_content_availability(db: Session, content_id: int, region: str = "US", refresh_if_old: bool = True):
    
    # Check cache
    availability_records = db.query(StreamingAvailability).filter(
        StreamingAvailability.content_id == content_id,
        StreamingAvailability.region == region
    ).all()
    
    # check records they're fresh
    if availability_records:
        # Check if oldest entry is less than 7 days old
        oldest = min(a.last_checked for a in availability_records)
        cache_age = datetime.utcnow() - oldest
        
        if cache_age < timedelta(days=7):
            # Cache is fresh, return it
            platforms = [a.platform for a in availability_records if a.platform_id is not None]
            return {
                "cached": True,
                "cache_age_days": cache_age.days,
                "platforms": platforms
            }
        elif not refresh_if_old:
            platforms = [a.platform for a in availability_records if a.platform_id is not None]
            return {
                "cached": True,
                "cache_age_days": cache_age.days,
                "stale": True,
                "platforms": platforms
            }
    
    # fetch fresh data
    content = db.query(Content).filter(Content.id == content_id).first()
    
    if not content:
        return {
            "cached": False,
            "platforms": []
        }
    
    # Fetch and cache new data
    platform_ids = update_content_availability(db, content_id, content.type, region)
    
    # Get platform objects
    platforms = db.query(Platform).filter(Platform.id.in_(platform_ids)).all() if platform_ids else []
    
    return {
        "cached": False,
        "platforms": platforms
    }