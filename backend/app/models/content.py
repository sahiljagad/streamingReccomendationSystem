from sqlalchemy import Column, Integer, String, Float, Text, TIMESTAMP, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Content(Base):
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True)  # TMDB ID
    title = Column(String(500), nullable=False)
    type = Column(String(20), nullable=False)  # 'movie' or 'tv'
    release_year = Column(Integer, nullable=True)
    genres = Column(JSON, nullable=True)
    overview = Column(Text, nullable=True)
    poster_path = Column(String(255), nullable=True)
    backdrop_path = Column(String(255), nullable=True)
    tmdb_rating = Column(Float, nullable=True)
    runtime = Column(Integer, nullable=True)
    director = Column(String(255), nullable=True)
    cast = Column(JSON, nullable=True)
    content_rating = Column(String(10), nullable=True)
    trailer_url = Column(String(255), nullable=True)
    language = Column(String(10), default='en')
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user_interactions = relationship("UserContent", back_populates="content", cascade="all, delete-orphan")
    availability = relationship("StreamingAvailability", back_populates="content", cascade="all, delete-orphan")