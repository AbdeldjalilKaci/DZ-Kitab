# app/models/user_suspension.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime, timedelta

class UserSuspension(Base):
    __tablename__ = "user_suspensions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    reason = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    suspended_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    suspension_end_date = Column(DateTime(timezone=True), nullable=False)
    
    zero_rating_count = Column(Integer, default=0)
    low_rating_count = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True, index=True)
    reactivated_at = Column(DateTime(timezone=True), nullable=True)
    
    created_by_admin = Column(Boolean, default=False)
    admin_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relation avec lazy="select"
    user = relationship("User", back_populates="suspensions", lazy="select")
    
    def is_expired(self) -> bool:
        if not self.is_active:
            return True
        return datetime.utcnow() > self.suspension_end_date
    
    def reactivate(self):
        self.is_active = False
        self.reactivated_at = datetime.utcnow()
    
    @staticmethod
    def create_low_rating_suspension(user_id: int, zero_rating_count: int, duration_days: int = 15):
        return UserSuspension(
            user_id=user_id,
            reason="low_ratings",
            description=f"Suspension automatique: {zero_rating_count} notes à 0 étoile",
            suspension_end_date=datetime.utcnow() + timedelta(days=duration_days),
            zero_rating_count=zero_rating_count,
            created_by_admin=False
        )
    
    @staticmethod
    def create_manual_suspension(user_id: int, duration_days: int, reason: str, admin_notes: str = None):
        return UserSuspension(
            user_id=user_id,
            reason="manual",
            description=reason,
            suspension_end_date=datetime.utcnow() + timedelta(days=duration_days),
            created_by_admin=True,
            admin_notes=admin_notes
        )
    
    def __repr__(self):
        return f"<UserSuspension(id={self.id}, user_id={self.user_id}, reason={self.reason}, active={self.is_active})>"


class RatingAlert(Base):
    __tablename__ = "rating_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    alert_type = Column(String, nullable=False)
    
    low_rating_count = Column(Integer, default=0)
    zero_rating_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relation avec lazy="select"
    user = relationship("User", back_populates="rating_alerts", lazy="select")
    
    def __repr__(self):
        return f"<RatingAlert(id={self.id}, user_id={self.user_id}, type={self.alert_type})>"
