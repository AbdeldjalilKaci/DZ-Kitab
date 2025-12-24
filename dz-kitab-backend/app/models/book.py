# app/models/book.py

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class BookConditionEnum(enum.Enum):
    NEUF = "Neuf"
    COMME_NEUF = "Comme neuf"
    BON_ETAT = "Bon état"
    ETAT_ACCEPTABLE = "État acceptable"
    USAGE = "Usagé"

class AnnouncementStatusEnum(enum.Enum):
    ACTIVE = "Active"
    VENDU = "Vendu"
    RESERVE = "Réservé"
    DESACTIVE = "Désactivé"

class BookCategoryEnum(enum.Enum):
    INFORMATIQUE = "Informatique"
    MATHEMATIQUES = "Mathématiques"
    PHYSIQUE = "Physique"
    CHIMIE = "Chimie"
    BIOLOGIE = "Biologie"
    MEDECINE = "Médecine"
    ECONOMIE = "Économie"
    GESTION = "Gestion"
    DROIT = "Droit"
    LANGUES = "Langues"
    LITTERATURE = "Littérature"
    HISTOIRE = "Histoire"
    GEOGRAPHIE = "Géographie"
    PHILOSOPHIE = "Philosophie"
    PSYCHOLOGIE = "Psychologie"
    ARCHITECTURE = "Architecture"
    INGENIERIE = "Ingénierie"
    AUTRE = "Autre"

class Book(Base):
    """Table pour stocker les informations des livres (depuis Google Books API)"""
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    subtitle = Column(String, nullable=True)
    authors = Column(String, nullable=True)
    publisher = Column(String, nullable=True)
    published_date = Column(String, nullable=True)  # Année de publication
    description = Column(Text, nullable=True)
    page_count = Column(Integer, nullable=True)  # Nombre de pages du livre
    categories = Column(String, nullable=True)
    language = Column(String, default="fr")
    cover_image_url = Column(String, nullable=True)
    preview_link = Column(String, nullable=True)
    info_link = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    announcements = relationship("Announcement", back_populates="book")

    def __repr__(self):
        return f"<Book(id={self.id}, isbn={self.isbn}, title={self.title})>"

class Announcement(Base):
    """Table pour les annonces de vente de livres"""
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Prix et condition
    price = Column(Float, nullable=False)
    market_price = Column(Float, nullable=True)  # Prix du marché pour référence
    final_calculated_price = Column(Float, nullable=True)  # Prix final calculé avec le score de condition
    condition = Column(Enum(BookConditionEnum), nullable=False)
    
    # Catégorie choisie par l'utilisateur
    category = Column(Enum(BookCategoryEnum), nullable=False)
    
    # Statut
    status = Column(Enum(AnnouncementStatusEnum), default=AnnouncementStatusEnum.ACTIVE)
    
    # Détails
    description = Column(Text, nullable=True)
    custom_images = Column(String, nullable=True)
    location = Column(String, nullable=True)
    
    # Informations sur le livre (peut être différent de Book si l'utilisateur le modifie)
    page_count = Column(Integer, nullable=True)  # Nombre de pages saisi/modifié par l'utilisateur
    publication_date = Column(String, nullable=True)  # Date de publication saisie/modifiée
    
    # Statistiques
    views_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    book = relationship("Book", back_populates="announcements")
    user = relationship("User", back_populates="announcements")
    condition_score = relationship("BookConditionScore", back_populates="announcement", uselist=False)
    ratings = relationship(
        "Rating",
        back_populates="announcement",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Announcement(id={self.id}, book_id={self.book_id}, price={self.price})>"
