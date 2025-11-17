from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserPlatform(Base):
    __tablename__ = "user_platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.id", ondelete="CASCADE"), nullable=False)
    added_at = Column(TIMESTAMP, server_default=func.now())
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('user_id', 'platform_id', name='_user_platform_uc'),)
    
    # Relationships
    user = relationship("User", back_populates="platforms")
    platform = relationship("Platform", back_populates="user_platforms")