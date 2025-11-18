from sqlalchemy.orm import Session
from app.models.platform import Platform


def seed_platforms(db: Session):
    platforms = [
        {
            "name": "netflix",
            "display_name": "Netflix",
            "website_url": "https://www.netflix.com"
        },
        {
            "name": "prime",
            "display_name": "Prime Video",
            "website_url": "https://www.amazon.com/primevideo"
        },
        {
            "name": "disney",
            "display_name": "Disney+",
            "website_url": "https://www.disneyplus.com"
        }
    ]
    
    for platform_data in platforms:
        # Check if platform already exists
        existing = db.query(Platform).filter(Platform.name == platform_data["name"]).first()
        if not existing:
            platform = Platform(**platform_data)
            db.add(platform)
    
    db.commit()
    print("Platforms seeded successfully")


if __name__ == "__main__":
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        seed_platforms(db)
    finally:
        db.close()