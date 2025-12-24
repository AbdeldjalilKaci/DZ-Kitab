# app/models/user_suspension.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime, timedelta

class UserSuspension(Base):
    """Table pour gérer les suspensions de compte utilisateur"""
    __tablename__ = "user_suspensions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Raison et détails
    reason = Column(String, nullable=False)  # "low_ratings", "violation", "manual"
    description = Column(Text, nullable=True)  # Description détaillée
    
    # Période de suspension
    suspended_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    suspension_end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Métadonnées
    zero_rating_count = Column(Integer, default=0)  # Nombre de notes à 0
    low_rating_count = Column(Integer, default=0)   # Nombre de notes <= 1
    
    # Statut
    is_active = Column(Boolean, default=True, index=True)  # True si suspension en cours
    reactivated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Qui a créé la suspension
    created_by_admin = Column(Boolean, default=False)
    admin_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relation
    user = relationship("User", back_populates="suspensions")
    
    def is_expired(self) -> bool:
        """Vérifier si la suspension est expirée"""
        if not self.is_active:
            return True
        return datetime.utcnow() > self.suspension_end_date
    
    def reactivate(self):
        """Réactiver le compte après la suspension"""
        self.is_active = False
        self.reactivated_at = datetime.utcnow()
    
    @staticmethod
    def create_low_rating_suspension(user_id: int, zero_rating_count: int, duration_days: int = 15):
        """Créer une suspension pour notes basses"""
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
        """Créer une suspension manuelle par un admin"""
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
    """Table pour suivre les alertes de notes basses"""
    __tablename__ = "rating_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Type d'alerte
    alert_type = Column(String, nullable=False)  # "low_rating_warning", "suspension_imminent"
    
    # Données de l'alerte
    low_rating_count = Column(Integer, default=0)
    zero_rating_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    
    # Email envoyé
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relation
    user = relationship("User", back_populates="rating_alerts")
    
    def __repr__(self):
        return f"<RatingAlert(id={self.id}, user_id={self.user_id}, type={self.alert_type})>"
