from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserMiniResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

class BookCondition(str, Enum):
    NEUF = "Neuf"
    COMME_NEUF = "Comme neuf"
    BON_ETAT = "Bon état"
    ETAT_ACCEPTABLE = "État acceptable"
    USAGE = "Usagé"

class AnnouncementStatus(str, Enum):
    ACTIVE = "Active"
    VENDU = "Vendu"
    RESERVE = "Réservé"
    DESACTIVE = "Désactivé"

class BookCategory(str, Enum):
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

class GoogleBookInfo(BaseModel):
    """Response from Google Books API"""
    isbn: str
    title: str
    subtitle: Optional[str] = None
    authors: List[str] = []
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    description: Optional[str] = None
    page_count: Optional[int] = None
    categories: List[str] = []
    language: str = "fr"
    cover_image_url: Optional[str] = None
    preview_link: Optional[str] = None
    info_link: Optional[str] = None

class BookBase(BaseModel):
    isbn: str
    title: str
    subtitle: Optional[str] = None
    authors: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    description: Optional[str] = None
    page_count: Optional[int] = None
    categories: Optional[str] = None
    language: str = "fr"
    cover_image_url: Optional[str] = None
    preview_link: Optional[str] = None
    info_link: Optional[str] = None

class BookResponse(BookBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AnnouncementCreate(BaseModel):
    isbn: str = Field(..., description="ISBN du livre")
    category: BookCategory = Field(..., description="Catégorie du livre")
    price: float = Field(..., gt=0, description="Prix de vente en DZD")
    market_price: Optional[float] = Field(None, gt=0, description="Prix du marché en DZD")
    condition: BookCondition
    description: Optional[str] = Field(None, max_length=1000)
    location: Optional[str] = Field(None, max_length=200)
    custom_images: Optional[List[str]] = None
    page_count: Optional[int] = Field(None, gt=0, description="Nombre de pages")
    publication_date: Optional[str] = Field(None, description="Date/Année de publication")
    
    # Optional fields for manual book entry if Google Books fails
    title: Optional[str] = None
    authors: Optional[str] = None
    publisher: Optional[str] = None
    cover_image_url: Optional[str] = None


    @validator('isbn')
    def validate_isbn(cls, v):
        clean_isbn = v.replace("-", "").replace(" ", "")
        if len(clean_isbn) not in [10, 13]:
            raise ValueError("L'ISBN doit contenir 10 ou 13 chiffres")
        if not clean_isbn.isdigit():
            raise ValueError("L'ISBN ne doit contenir que des chiffres")
        return clean_isbn

class AnnouncementUpdate(BaseModel):
    category: Optional[BookCategory] = None
    price: Optional[float] = Field(None, gt=0)
    market_price: Optional[float] = Field(None, gt=0)
    condition: Optional[BookCondition] = None
    description: Optional[str] = Field(None, max_length=1000)
    location: Optional[str] = Field(None, max_length=200)
    status: Optional[AnnouncementStatus] = None
    custom_images: Optional[List[str]] = None
    page_count: Optional[int] = Field(None, gt=0)
    publication_date: Optional[str] = None

class AnnouncementResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    category: str
    price: float
    market_price: Optional[float] = None
    final_calculated_price: Optional[float] = None
    condition: str
    status: str
    description: Optional[str] = None
    custom_images: Optional[str] = None
    location: Optional[str] = None
    page_count: Optional[int] = None
    publication_date: Optional[str] = None
    views_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    book: BookResponse
    user: UserMiniResponse


    class Config:
        from_attributes = True

class AnnouncementListResponse(BaseModel):
    total: int
    announcements: List[AnnouncementResponse]

class ISBNLookupResponse(BaseModel):
    found: bool
    book_info: Optional[GoogleBookInfo] = None
    message: Optional[str] = None

class PriceCalculationResponse(BaseModel):
    """Réponse du calcul du prix final avec le score de condition"""
    market_price: float
    condition_score: float  # Score en pourcentage (0-100)
    calculated_price: float  # Prix final calculé
    price_breakdown: dict  # Détails du calcul
