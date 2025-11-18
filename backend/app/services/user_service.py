from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user_platform import UserPlatform
from app.models.platform import Platform


def get_user_platforms(db: Session, user_id: int) -> list[Platform]:
    user_platforms = (
        db.query(Platform)
        .join(UserPlatform)
        .filter(UserPlatform.user_id == user_id)
        .all()
    )
    return user_platforms


def update_user_platforms(db: Session, user_id: int, platform_ids: list[int]) -> list[Platform]:

    # Validate that all platform_ids exist
    platforms = db.query(Platform).filter(Platform.id.in_(platform_ids)).all()
    
    if len(platforms) != len(platform_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more invalid platform IDs"
        )
    
    # Delete existing user platforms
    db.query(UserPlatform).filter(UserPlatform.user_id == user_id).delete()
    
    # Add new user platforms
    for platform_id in platform_ids:
        user_platform = UserPlatform(user_id=user_id, platform_id=platform_id)
        db.add(user_platform)
    
    db.commit()
    
    # Return updated platforms
    return get_user_platforms(db, user_id)


def get_all_platforms(db: Session) -> list[Platform]:
    platforms = db.query(Platform).filter(Platform.active == True).all()
    return platforms