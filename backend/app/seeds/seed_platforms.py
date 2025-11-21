from sqlalchemy.orm import Session
from app.models.platform import Platform


def seed_platforms(db: Session):
    # Seed initial streaming platforms
    platforms = [
        {
            "name": "netflix",
            "display_name": "Netflix",
            "website_url": "https://www.netflix.com",
            "tmdb_provider_id": 8
        },
        {
            "name": "prime",
            "display_name": "Prime Video",
            "website_url": "https://www.amazon.com/primevideo",
            "tmdb_provider_id": 9
        },
        {
            "name": "disney",
            "display_name": "Disney+",
            "website_url": "https://www.disneyplus.com",
            "tmdb_provider_id": 337
        }
    ]
    
    for platform_data in platforms:
        # Check if platform already exists
        existing = db.query(Platform).filter(Platform.name == platform_data["name"]).first()
        if existing:
            # Update with TMDB provider ID
            existing.tmdb_provider_id = platform_data["tmdb_provider_id"]
        else:
            platform = Platform(**platform_data)
            db.add(platform)
    
    db.commit()
    print("Platforms seeded/updated successfully")


if __name__ == "__main__":
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        seed_platforms(db)
    finally:
        db.close()