# app/models/notification.py

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class NotificationType(enum.Enum):
    NEW_RATING = "new_rating"
    RATING_REPLY = "rating_reply"
    ANNOUNCEMENT_SOLD = "announcement_sold"
    ANNOUNCEMENT_RESERVED = "announcement_reserved"
    LOW_RATING_ALERT = "low_rating_alert"
    ACCOUNT_SUSPENDED = "account_suspended"
    ACCOUNT_REACTIVATED = "account_reactivated"
    MESSAGE_RECEIVED = "message_received"
    PRICE_DROP = "price_drop"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    
    related_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    related_announcement_id = Column(Integer, ForeignKey("announcements.id", ondelete="SET NULL"), nullable=True)
    related_rating_id = Column(Integer, ForeignKey("ratings.id", ondelete="SET NULL"), nullable=True)
    
    action_url = Column(String, nullable=True)
    is_read = Column(Boolean, default=False, index=True)
    is_sent_email = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relations avec lazy="select"
    user = relationship("User", foreign_keys=[user_id], back_populates="notifications", lazy="select")
    related_user = relationship("User", foreign_keys=[related_user_id], lazy="select")
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = func.now()
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type.value}, read={self.is_read})>"


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    email_new_rating = Column(Boolean, default=True)
    email_rating_reply = Column(Boolean, default=True)
    email_announcement_sold = Column(Boolean, default=True)
    email_low_rating_alert = Column(Boolean, default=True)
    email_account_suspended = Column(Boolean, default=True)
    email_message_received = Column(Boolean, default=True)
    app_notifications_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relation avec lazy="select"
    user = relationship("User", back_populates="notification_preferences", lazy="select")
    
    def __repr__(self):
        return f"<NotificationPreference(user_id={self.user_id})>"
