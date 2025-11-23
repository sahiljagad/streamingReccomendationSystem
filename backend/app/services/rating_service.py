from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException, status
from app.models.user_content import UserContent
from app.models.content import Content
from app.models.platform import Platform


def rate_content(
    db: Session,
    user_id: int,
    content_id: int,
    rating: int = None,
    watch_status: str = None,
    watched_on_platform_id: int = None
):
    
    # Validate rating if provided
    if rating is not None and (rating < 1 or rating > 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    # Validate watch status if provided
    valid_statuses = ['watched', 'want_to_watch', 'not_interested']
    if watch_status and watch_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Verify content exists
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Verify platform exists if provided
    if watched_on_platform_id:
        platform = db.query(Platform).filter(Platform.id == watched_on_platform_id).first()
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Platform not found"
            )
    
    # Check if user already has a rating for this content
    user_content = db.query(UserContent).filter(
        UserContent.user_id == user_id,
        UserContent.content_id == content_id
    ).first()
    
    if user_content:
        # Update existing rating
        if rating is not None:
            user_content.rating = rating
        if watch_status:
            user_content.status = watch_status
        if watched_on_platform_id is not None:
            user_content.watched_on_platform_id = watched_on_platform_id
        user_content.updated_at = datetime.utcnow()
    else:
        # Create new rating
        # Default status to 'watched' if user rating it
        if not watch_status:
            watch_status = 'watched' if rating else 'want_to_watch'
        
        user_content = UserContent(
            user_id=user_id,
            content_id=content_id,
            rating=rating,
            status=watch_status,
            watched_on_platform_id=watched_on_platform_id
        )
        db.add(user_content)
    
    db.commit()
    db.refresh(user_content)
    
    return user_content


def get_user_ratings(
    db: Session,
    user_id: int,
    status_filter: str = None,
    limit: int = 100,
    offset: int = 0
):
    
    query = db.query(UserContent).filter(UserContent.user_id == user_id)
    
    # Filter by status if provided
    if status_filter:
        valid_statuses = ['watched', 'want_to_watch', 'not_interested']
        if status_filter not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter. Must be one of: {', '.join(valid_statuses)}"
            )
        query = query.filter(UserContent.status == status_filter)
    
    # Order by most recently updated
    query = query.order_by(UserContent.updated_at.desc())
    
    # Paginate
    total = query.count()
    ratings = query.limit(limit).offset(offset).all()
    
    return {
        "ratings": ratings,
        "total": total,
        "limit": limit,
        "offset": offset
    }


def get_content_rating(db: Session, user_id: int, content_id: int):
    
    user_content = db.query(UserContent).filter(
        UserContent.user_id == user_id,
        UserContent.content_id == content_id
    ).first()
    
    return user_content


def delete_rating(db: Session, user_id: int, content_id: int):
    
    user_content = db.query(UserContent).filter(
        UserContent.user_id == user_id,
        UserContent.content_id == content_id
    ).first()
    
    if not user_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    
    db.delete(user_content)
    db.commit()
    
    return {"message": "Rating deleted successfully"}