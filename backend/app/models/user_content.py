from sqlalchemy import Column, Integer, ForeignKey, String, CheckConstraint, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserContent(Base):
    __tablename__ = "user_content"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False)  # 'watched', 'want_to_watch', 'not_interested'
    watched_on_platform_id = Column(Integer, ForeignKey("platforms.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'content_id', name='_user_content_uc'),
        CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range_check'),
    )
    
    # Relationships
    user = relationship("User", back_populates="content_interactions")
    content = relationship("Content", back_populates="user_interactions")
    platform = relationship("Platform")