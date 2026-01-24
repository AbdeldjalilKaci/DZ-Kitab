# app/models/user.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UniversityEnum(enum.Enum):
    ESTIN = "ESTIN"
    ESI = "ESI"
    EPAU = "EPAU"
    USTHB = "USTHB"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    university = Column(Enum(UniversityEnum), nullable=True)
    phone_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False, index=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    profile_picture_url = Column(String, nullable=True)
    # Relationships
    announcements = relationship(
        "Announcement", 
        back_populates="user", 
        cascade="all, delete-orphan",
        lazy="select"  # ✅ Chargement paresseux
    )

    # Rating relationships
    ratings_given = relationship(
        "Rating",
        foreign_keys="Rating.buyer_id",
        back_populates="buyer",
        cascade="all, delete-orphan",
        lazy="select"  # ✅ Chargement paresseux
    )

    ratings_received = relationship(
        "Rating",
        foreign_keys="Rating.seller_id",
        back_populates="seller",
        cascade="all, delete-orphan",
        lazy="select"  # ✅ Chargement paresseux
    )

    seller_stats = relationship(
        "SellerStats",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="select"  # ✅ Chargement paresseux
    )

    # Notification relationships
    notifications = relationship(
        "Notification",
        foreign_keys="Notification.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"  # ✅ Chargement paresseux
    )
    
    notification_preferences = relationship(
        "NotificationPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="select"  # ✅ Chargement paresseux
    )

    # Suspension relationships
    suspensions = relationship(
        "UserSuspension",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"  # ✅ Chargement paresseux
    )

    rating_alerts = relationship(
        "RatingAlert",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"  # ✅ Chargement paresseux
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"

