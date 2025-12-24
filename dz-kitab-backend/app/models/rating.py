
from sqlalchemy import Column, Integer, Text, Float, ForeignKey, DateTime, CheckConstraint, Boolean
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from app.database import Base

class Rating(Base):
    """Table pour les notes et commentaires des vendeurs"""
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    seller_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    announcement_id = Column(Integer, ForeignKey("announcements.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Notes
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    communication_rating = Column(Integer, nullable=True)
    condition_accuracy_rating = Column(Integer, nullable=True)
    delivery_speed_rating = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range'),
        CheckConstraint('buyer_id != seller_id', name='buyer_not_seller'),
        CheckConstraint('communication_rating IS NULL OR (communication_rating >= 1 AND communication_rating <= 5)', name='comm_rating_range'),
        CheckConstraint('condition_accuracy_rating IS NULL OR (condition_accuracy_rating >= 1 AND condition_accuracy_rating <= 5)', name='cond_rating_range'),
        CheckConstraint('delivery_speed_rating IS NULL OR (delivery_speed_rating >= 1 AND delivery_speed_rating <= 5)', name='delivery_rating_range'),
    )
    
    # Relations
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="ratings_given")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="ratings_received")
    announcement = relationship("Announcement", back_populates="ratings")
    
    def __repr__(self):
        return f"<Rating(id={self.id}, buyer_id={self.buyer_id}, seller_id={self.seller_id}, rating={self.rating})>"


class SellerStats(Base):
    """Statistiques agrégées pour chaque vendeur"""
    __tablename__ = "seller_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Statistiques
    total_ratings = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0, index=True)
    avg_communication = Column(Float, default=0.0)
    avg_condition_accuracy = Column(Float, default=0.0)
    avg_delivery_speed = Column(Float, default=0.0)
    
    # Distribution des notes
    rating_5_count = Column(Integer, default=0)
    rating_4_count = Column(Integer, default=0)
    rating_3_count = Column(Integer, default=0)
    rating_2_count = Column(Integer, default=0)
    rating_1_count = Column(Integer, default=0)
    
    # Badges
    is_top_seller = Column(Boolean, default=False)
    total_sales = Column(Integer, default=0)
    
    # Timestamp
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relation
    user = relationship("User", back_populates="seller_stats")
    
    def calculate_stats(self, db: Session):
        """Recalculer toutes les statistiques du vendeur"""
        ratings = db.query(Rating).filter(Rating.seller_id == self.user_id).all()
        
        if not ratings:
            self.total_ratings = 0
            self.average_rating = 0.0
            return
        
        self.total_ratings = len(ratings)
        
        # Calculer les moyennes
        self.average_rating = sum(r.rating for r in ratings) / len(ratings)
        
        comm_ratings = [r.communication_rating for r in ratings if r.communication_rating]
        self.avg_communication = sum(comm_ratings) / len(comm_ratings) if comm_ratings else 0.0
        
        cond_ratings = [r.condition_accuracy_rating for r in ratings if r.condition_accuracy_rating]
        self.avg_condition_accuracy = sum(cond_ratings) / len(cond_ratings) if cond_ratings else 0.0
        
        deliv_ratings = [r.delivery_speed_rating for r in ratings if r.delivery_speed_rating]
        self.avg_delivery_speed = sum(deliv_ratings) / len(deliv_ratings) if deliv_ratings else 0.0
        
        # Distribution
        self.rating_5_count = sum(1 for r in ratings if r.rating == 5)
        self.rating_4_count = sum(1 for r in ratings if r.rating == 4)
        self.rating_3_count = sum(1 for r in ratings if r.rating == 3)
        self.rating_2_count = sum(1 for r in ratings if r.rating == 2)
        self.rating_1_count = sum(1 for r in ratings if r.rating == 1)
        
        # Top seller: moyenne >= 4.5 et au moins 10 ventes
        self.is_top_seller = self.average_rating >= 4.5 and self.total_ratings >= 10
    
    def __repr__(self):
        return f"<SellerStats(user_id={self.user_id}, avg={self.average_rating:.2f}, total={self.total_ratings})>"
