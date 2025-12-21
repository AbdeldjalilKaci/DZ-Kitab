# app/models/book_condition.py

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class BookConditionScore(Base):
    """Table pour stocker les scores détaillés de l'état du livre"""
    __tablename__ = "book_condition_scores"

    id = Column(Integer, primary_key=True, index=True)
    announcement_id = Column(Integer, ForeignKey("announcements.id", ondelete="CASCADE"), unique=True)
    
    # PAGE SCORE (0-100)
    page_no_missing = Column(Boolean, default=False)  # Aucune page manquante
    page_no_torn = Column(Boolean, default=False)  # Pas de pages déchirées
    page_clean = Column(Boolean, default=False)  # Pages propres
    page_score = Column(Float, default=0.0)  # Score calculé /100
    
    # BINDING SCORE (0-100)
    binding_no_loose = Column(Boolean, default=False)  # Pas de fil/colle visible
    binding_no_falling = Column(Boolean, default=False)  # Pages ne tombent pas
    binding_stable = Column(Boolean, default=False)  # Reliure stable
    binding_score = Column(Float, default=0.0)
    
    # COVER SCORE (0-100)
    cover_no_detachment = Column(Boolean, default=False)  # Pas de détachement
    cover_clean = Column(Boolean, default=False)  # Couverture propre
    cover_no_scratches = Column(Boolean, default=False)  # Pas de rayures
    cover_score = Column(Float, default=0.0)
    
    # DAMAGES SCORE (0-100)
    damage_no_burns = Column(Boolean, default=False)  # Pas de brûlures/taches
    damage_no_smell = Column(Boolean, default=False)  # Pas d'odeur forte
    damage_no_insects = Column(Boolean, default=False)  # Pas de traces d'insectes
    damage_score = Column(Float, default=0.0)
    
    # ACCESSORIES SCORE (0-100)
    accessories_complete = Column(Boolean, default=False)  # Accessoires complets (CD, etc.)
    accessories_content = Column(Boolean, default=False)  # Contenu interne complet
    accessories_extras = Column(Boolean, default=False)  # Extras présents
    accessories_score = Column(Float, default=0.0)
    
    # OVERALL SCORE
    overall_score = Column(Float, default=0.0)  # Score global /100
    condition_label = Column(String)  # "Comme neuf", "Très bon état", etc.
    
    # PRICE SUGGESTION
    base_price = Column(Float, nullable=True)  # Prix moyen constaté
    suggested_price = Column(Float, nullable=True)  # Prix suggéré selon le score
    
    # AI ANALYSIS (optionnel)
    has_photos = Column(Boolean, default=False)
    ai_analysis = Column(JSON, nullable=True)  # Résultats de l'analyse IA
    photo_urls = Column(JSON, nullable=True)  # URLs des photos analysées
    
    # Relationship
    announcement = relationship("Announcement", back_populates="condition_score")

    def calculate_scores(self):
        """Calcule tous les scores automatiquement"""
        # Page Score (3 questions)
        page_checks = [self.page_no_missing, self.page_no_torn, self.page_clean]
        self.page_score = (sum(page_checks) / len(page_checks)) * 100
        
        # Binding Score (3 questions)
        binding_checks = [self.binding_no_loose, self.binding_no_falling, self.binding_stable]
        self.binding_score = (sum(binding_checks) / len(binding_checks)) * 100
        
        # Cover Score (3 questions)
        cover_checks = [self.cover_no_detachment, self.cover_clean, self.cover_no_scratches]
        self.cover_score = (sum(cover_checks) / len(cover_checks)) * 100
        
        # Damage Score (3 questions)
        damage_checks = [self.damage_no_burns, self.damage_no_smell, self.damage_no_insects]
        self.damage_score = (sum(damage_checks) / len(damage_checks)) * 100
        
        # Accessories Score (3 questions)
        accessories_checks = [self.accessories_complete, self.accessories_content, self.accessories_extras]
        self.accessories_score = (sum(accessories_checks) / len(accessories_checks)) * 100
        
        # Overall Score (moyenne pondérée)
        weights = {
            'page': 0.25,
            'binding': 0.20,
            'cover': 0.20,
            'damage': 0.25,
            'accessories': 0.10
        }
        
        self.overall_score = (
            self.page_score * weights['page'] +
            self.binding_score * weights['binding'] +
            self.cover_score * weights['cover'] +
            self.damage_score * weights['damage'] +
            self.accessories_score * weights['accessories']
        )
        
        # Déterminer le label de condition
        if self.overall_score >= 95:
            self.condition_label = "Comme neuf"
        elif self.overall_score >= 85:
            self.condition_label = "Très bon état"
        elif self.overall_score >= 70:
            self.condition_label = "Bon état"
        elif self.overall_score >= 50:
            self.condition_label = "État acceptable"
        else:
            self.condition_label = "Usagé"
        
        return self.overall_score
    
    def suggest_price(self, base_price: float = None):
        """Suggère un prix basé sur le score global"""
        if base_price:
            self.base_price = base_price
        
        if not self.base_price:
            return None
        
        # Calcul du multiplicateur basé sur le score
        if self.overall_score >= 95:
            multiplier = 1.0  # Prix plein
        elif self.overall_score >= 85:
            multiplier = 0.85
        elif self.overall_score >= 70:
            multiplier = 0.70
        elif self.overall_score >= 50:
            multiplier = 0.50
        else:
            multiplier = 0.35
        
        self.suggested_price = round(self.base_price * multiplier, 2)
        return self.suggested_price

    def __repr__(self):
        return f"<BookConditionScore(announcement_id={self.announcement_id}, overall={self.overall_score:.1f}%)>"