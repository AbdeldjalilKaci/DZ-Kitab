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


class Book(Base):
    """Table pour stocker les informations des livres (depuis Google Books API)"""
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    subtitle = Column(String, nullable=True)
    authors = Column(String, nullable=True)
    publisher = Column(String, nullable=True)
    published_date = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    page_count = Column(Integer, nullable=True)
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
    price = Column(Float, nullable=False)
    condition = Column(Enum(BookConditionEnum), nullable=False)
    status = Column(Enum(AnnouncementStatusEnum), default=AnnouncementStatusEnum.ACTIVE)
    description = Column(Text, nullable=True)
    custom_images = Column(String, nullable=True)
    location = Column(String, nullable=True)
    views_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    ratings = relationship("Rating", back_populates="announcement")
    # Relationships
    book = relationship("Book", back_populates="announcements")
    user = relationship("User", back_populates="announcements")
    condition_score = relationship("BookConditionScore", back_populates="announcement", uselist=False)
# Dans la classe Announcement
    ratings = relationship(
    "Rating",
    back_populates="announcement",
    cascade="all, delete-orphan"
)
    def __repr__(self):
        return f"<Announcement(id={self.id}, book_id={self.book_id}, price={self.price})>"
