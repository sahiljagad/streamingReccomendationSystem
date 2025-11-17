from sqlalchemy import Column, Integer, ForeignKey, String, Date, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class StreamingAvailability(Base):
    __tablename__ = "streaming_availability"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id", ondelete="CASCADE"), nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.id", ondelete="CASCADE"), nullable=False)
    region = Column(String(10), default='US')
    available_until = Column(Date, nullable=True)
    last_checked = Column(TIMESTAMP, server_default=func.now())
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('content_id', 'platform_id', 'region', name='_availability_uc'),)
    
    # Relationships
    content = relationship("Content", back_populates="availability")
    platform = relationship("Platform", back_populates="streaming_availability")