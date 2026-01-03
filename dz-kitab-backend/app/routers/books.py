# app/routers/books.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import httpx

from app.database import get_db
from app.models.book import Book, Announcement, BookCategoryEnum, BookConditionEnum, AnnouncementStatusEnum
from app.models.user import User
from app.schemas.book import (
    AnnouncementCreate,
    AnnouncementUpdate,
    AnnouncementResponse,
    AnnouncementListResponse,
    ISBNLookupResponse,
    GoogleBookInfo,
    BookResponse
)
from app.middleware.auth import security
from app.services.jwt import verify_token
from app.services.google_books import fetch_book_by_isbn

from app.core.errors import (
    ResourceNotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ValidationError,
    DatabaseError,
    ExternalServiceError
)
from app.core.logging_config import error_logger

router = APIRouter()


def get_current_user_id(token: str = Depends(security), db: Session = Depends(get_db)) -> int:
    """Get the current authenticated user ID from token"""
    payload = verify_token(token)
    if not payload:
        raise UnauthorizedError("Token invalide")
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise ResourceNotFoundError("Utilisateur", email)
    
    return user.id


# ============================================
# CATEGORIES
# ============================================

@router.get("/categories", response_model=List[str])
def get_categories():
    """
    Obtenir la liste de toutes les catégories disponibles
    """
    return [category.value for category in BookCategoryEnum]


# ============================================
# ISBN LOOKUP - AUTO-FILL BOOK INFO
# ============================================

@router.get("/isbn/test", response_model=ISBNLookupResponse)
async def test_isbn_lookup():
    """
    Test endpoint with mock data - no real API call
    Use this to test the frontend while Google Books API has issues
    """
    mock_book = GoogleBookInfo(
        isbn="9782100545476",
        title="Mathématiques pour l'ingénieur",
        subtitle="Rappels de cours et exercices corrigés",
        authors=["Jean-Pierre Ramis", "André Warusfel"],
        publisher="Dunod",
        published_date="2009",
        description="Cet ouvrage présente les bases mathématiques indispensables aux futurs ingénieurs...",
        page_count=542,
        categories=["Mathematics", "Engineering"],
        language="fr",
        cover_image_url="https://books.google.com/books/content?id=TEST&printsec=frontcover&img=1&zoom=1",
        preview_link="https://books.google.com/books?id=TEST",
        info_link="https://books.google.com/books?id=TEST"
    )
    
    return ISBNLookupResponse(
        found=True,
        book_info=mock_book,
        message="Données de test (Google Books API indisponible)"
    )


@router.get("/isbn/{isbn}", response_model=ISBNLookupResponse)
async def lookup_isbn(isbn: str):
    """
    Lookup book information by ISBN using Google Books API
    """
    try:
        book_info = await fetch_book_by_isbn(isbn)
        
        if not book_info:
            return ISBNLookupResponse(
                found=False,
                message=f"Aucun livre trouvé pour l'ISBN: {isbn}. Vérifiez que l'ISBN est correct ou essayez un autre ISBN."
            )
        
        return ISBNLookupResponse(
            found=True,
            book_info=GoogleBookInfo(**book_info)
        )
        
    except httpx.HTTPError as e:
        raise ExternalServiceError(
            "Google Books API",
            "L'API Google Books est temporairement indisponible. Veuillez réessayer."
        )
    except Exception as e:
        error_logger.log_error(
            error_type="ExternalServiceError",
            message=f"Erreur lors de la recherche ISBN: {str(e)}",
            status_code=500,
            extra_data={"isbn": isbn}
        )
        raise ExternalServiceError("Google Books API")


# ============================================
# CREATE ANNOUNCEMENT
# ============================================

@router.post("/announcements", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    announcement_data: AnnouncementCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Create a new book announcement with category, page count and publication date
    
    This endpoint:
    1. Fetches book info from Google Books API using the ISBN
    2. Creates or retrieves the book in the database
    3. Creates the announcement with category, page count, publication date
    """
    try:
        print(f"📖 Creating announcement for ISBN: {announcement_data.isbn}")
        print(f"📦 Data: {announcement_data.dict(exclude={'custom_images'})}")
        
        # 1. Fetch book info from Google Books
        book_info = await fetch_book_by_isbn(announcement_data.isbn)
        
        # 2. Check if book already exists in database
        isbn_to_use = announcement_data.isbn.replace("-", "").replace(" ", "")
        book = db.query(Book).filter(Book.isbn == isbn_to_use).first()
        
        if not book:
            if not book_info:
                # If not found on Google Books, we must have manual title and authors
                if not announcement_data.title:
                    raise ValidationError(
                        f"Aucun livre trouvé pour l'ISBN: {announcement_data.isbn}. "
                        "Veuillez fournir le titre et l'auteur manuellement."
                    )
                
                # Create new book entry from manual data
                book = Book(
                    isbn=isbn_to_use,
                    title=announcement_data.title,
                    authors=announcement_data.authors or "Auteur Inconnu",
                    publisher=announcement_data.publisher,
                    published_date=announcement_data.publication_date,
                    description=announcement_data.description,
                    page_count=announcement_data.page_count,
                    cover_image_url=announcement_data.cover_image_url,
                )
            else:
                # Create new book entry with info from Google Books
                book = Book(
                    isbn=book_info["isbn"],
                    title=book_info["title"],
                    subtitle=book_info.get("subtitle"),
                    authors=", ".join(book_info.get("authors", [])),
                    publisher=book_info.get("publisher"),
                    published_date=book_info.get("published_date"),
                    description=book_info.get("description"),
                    page_count=book_info.get("page_count"),
                    categories=", ".join(book_info.get("categories", [])),
                    language=book_info.get("language", "fr"),
                    cover_image_url=book_info.get("cover_image_url"),
                    preview_link=book_info.get("preview_link"),
                    info_link=book_info.get("info_link")
                )
            db.add(book)
            db.commit()
            db.refresh(book)
        
        # 3. Use page_count and publication_date from user input or fallback to book data
        page_count = announcement_data.page_count or book.page_count
        publication_date = announcement_data.publication_date or book.published_date
        
        # 4. Create announcement with new fields
        custom_images_str = None
        if announcement_data.custom_images:
            custom_images_str = ",".join(announcement_data.custom_images)
        
        # Ensure we use enum values that match the database expectation
        announcement = Announcement(
            book_id=book.id,
            user_id=user_id,
            category=announcement_data.category.value,
            price=announcement_data.price,
            market_price=announcement_data.market_price,
            condition=announcement_data.condition.value,
            description=announcement_data.description,
            location=announcement_data.location,
            custom_images=custom_images_str,
            page_count=page_count,
            publication_date=publication_date
        )
        
        db.add(announcement)
        db.commit()
        db.refresh(announcement)

        # 5. Prepare response with nested data
        user = db.query(User).filter(User.id == user_id).first()
        
        # Safe enum to string conversion
        def get_val(obj):
            if hasattr(obj, 'value'):
                return obj.value
            return str(obj)

        return AnnouncementResponse(
            id=announcement.id,
            book_id=announcement.book_id,
            user_id=announcement.user_id,
            category=get_val(announcement.category),
            price=announcement.price,
            market_price=announcement.market_price,
            final_calculated_price=announcement.final_calculated_price,
            condition=get_val(announcement.condition),
            status=get_val(announcement.status),
            description=announcement.description,
            custom_images=announcement.custom_images,
            location=announcement.location,
            page_count=announcement.page_count,
            publication_date=announcement.publication_date,
            views_count=announcement.views_count or 0,
            created_at=announcement.created_at,
            updated_at=announcement.updated_at,
            book=BookResponse(
                id=book.id,
                isbn=book.isbn,
                title=book.title,
                subtitle=book.subtitle,
                authors=book.authors,
                publisher=book.publisher,
                published_date=book.published_date,
                description=book.description,
                page_count=book.page_count,
                categories=book.categories,
                language=book.language,
                cover_image_url=book.cover_image_url,
                preview_link=book.preview_link,
                info_link=book.info_link,
                created_at=book.created_at
            ),
            user=user
        )
        
    except IntegrityError as e:
        db.rollback()
        error_logger.log_error(
            error_type="IntegrityError",
            message="Contrainte d'intégrité violée",
            status_code=409,
            extra_data={"isbn": announcement_data.isbn}
        )
        raise  # Le handler global s'en charge
        
    except ValidationError:
        # Re-raise les ValidationError sans les wrapper
        raise
        
    except ExternalServiceError:
        # Re-raise les ExternalServiceError sans les wrapper
        raise
        
    except Exception as e:
        db.rollback()
        error_logger.log_error(
            error_type=type(e).__name__,
            message=str(e),
            status_code=500,
            extra_data={"isbn": announcement_data.isbn}
        )
        raise DatabaseError("Erreur lors de la création de l'annonce")


# ============================================
# GET ANNOUNCEMENTS
# ============================================

@router.get("/announcements", response_model=AnnouncementListResponse)
def get_announcements(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    condition: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of all active announcements (public endpoint)
    
    Optional filters:
    - status: Filter by announcement status
    - condition: Filter by book condition
    - category: Filter by book category
    """
    try:
        query = db.query(Announcement)
        
        # Apply filters
        if status:
            query = query.filter(Announcement.status == status)
        if condition:
            query = query.filter(Announcement.condition == condition)
        if category:
            query = query.filter(Announcement.category == category)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        announcements = query.offset(skip).limit(limit).all()
        
        # Format response
        formatted_announcements = []
        for ann in announcements:
            book = db.query(Book).filter(Book.id == ann.book_id).first()
            user = db.query(User).filter(User.id == ann.user_id).first()
            
            formatted_announcements.append(
                AnnouncementResponse(
                    id=ann.id,
                    book_id=ann.book_id,
                    user_id=ann.user_id,
                    category=ann.category.value,
                    price=ann.price,
                    market_price=ann.market_price,
                    final_calculated_price=ann.final_calculated_price,
                    condition=ann.condition.value,
                    status=ann.status.value,
                    description=ann.description,
                    custom_images=ann.custom_images,
                    location=ann.location,
                    page_count=ann.page_count,
                    publication_date=ann.publication_date,
                    views_count=ann.views_count,
                    created_at=ann.created_at,
                    updated_at=ann.updated_at,
                    book=book,
                    user={
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    }
                )
            )
        
        return AnnouncementListResponse(
            total=total,
            announcements=formatted_announcements
        )
        
    except Exception as e:
        error_logger.log_error(
            error_type=type(e).__name__,
            message=f"Erreur lors de la récupération des annonces: {str(e)}",
            status_code=500
        )
        raise DatabaseError("Erreur lors de la récupération des annonces")


@router.get("/announcements/{announcement_id}", response_model=AnnouncementResponse)
def get_announcement(announcement_id: int, db: Session = Depends(get_db)):
    """Get a specific announcement by ID"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not announcement:
        raise ResourceNotFoundError("Annonce", announcement_id)
    
    # Increment view count
    announcement.views_count += 1
    db.commit()
    
    book = db.query(Book).filter(Book.id == announcement.book_id).first()
    user = db.query(User).filter(User.id == announcement.user_id).first()
    
    return AnnouncementResponse(
        id=announcement.id,
        book_id=announcement.book_id,
        user_id=announcement.user_id,
        category=announcement.category.value,
        price=announcement.price,
        market_price=announcement.market_price,
        final_calculated_price=announcement.final_calculated_price,
        condition=announcement.condition.value,
        status=announcement.status.value,
        description=announcement.description,
        custom_images=announcement.custom_images,
        location=announcement.location,
        page_count=announcement.page_count,
        publication_date=announcement.publication_date,
        views_count=announcement.views_count,
        created_at=announcement.created_at,
        updated_at=announcement.updated_at,
        book=book,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    )


# ============================================
# MY ANNOUNCEMENTS
# ============================================

@router.get("/my-announcements", response_model=AnnouncementListResponse)
def get_my_announcements(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get all announcements created by the current user (protected route)"""
    announcements = db.query(Announcement).filter(Announcement.user_id == user_id).all()
    
    formatted_announcements = []
    for ann in announcements:
        book = db.query(Book).filter(Book.id == ann.book_id).first()
        user = db.query(User).filter(User.id == ann.user_id).first()
        
        formatted_announcements.append(
            AnnouncementResponse(
                id=ann.id,
                book_id=ann.book_id,
                user_id=ann.user_id,
                category=ann.category.value,
                price=ann.price,
                market_price=ann.market_price,
                final_calculated_price=ann.final_calculated_price,
                condition=ann.condition.value,
                status=ann.status.value,
                description=ann.description,
                custom_images=ann.custom_images,
                location=ann.location,
                page_count=ann.page_count,
                publication_date=ann.publication_date,
                views_count=ann.views_count,
                created_at=ann.created_at,
                updated_at=ann.updated_at,
                book=book,
                user={
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            )
        )
    
    return AnnouncementListResponse(
        total=len(formatted_announcements),
        announcements=formatted_announcements
    )


# ============================================
# UPDATE ANNOUNCEMENT
# ============================================
@router.put("/announcements/{announcement_id}", response_model=AnnouncementResponse)
def update_announcement(
    announcement_id: int,
    update_data: AnnouncementUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Update an announcement (only by the owner)"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not announcement:
        raise ResourceNotFoundError("Annonce", announcement_id)
    
    # Check ownership
    if announcement.user_id != user_id:
        raise ForbiddenError(
            "Vous n'êtes pas autorisé à modifier cette annonce. "
            "Seul le propriétaire peut modifier une annonce."
        )
    
    # Update fields
    if update_data.category is not None:
        announcement.category = update_data.category.value
    if update_data.price is not None:
        announcement.price = update_data.price
    if update_data.market_price is not None:
        announcement.market_price = update_data.market_price
    if update_data.condition is not None:
        announcement.condition = update_data.condition.value
    if update_data.description is not None:
        announcement.description = update_data.description
    if update_data.location is not None:
        announcement.location = update_data.location
    if update_data.status is not None:
        announcement.status = update_data.status.value
    if update_data.custom_images is not None:
        announcement.custom_images = ",".join(update_data.custom_images)
    if update_data.page_count is not None:
        announcement.page_count = update_data.page_count
    if update_data.publication_date is not None:
        announcement.publication_date = update_data.publication_date
    
    db.commit()
    db.refresh(announcement)
    
    book = db.query(Book).filter(Book.id == announcement.book_id).first()
    user = db.query(User).filter(User.id == announcement.user_id).first()
    
    return AnnouncementResponse(
        id=announcement.id,
        book_id=announcement.book_id,
        user_id=announcement.user_id,
        category=announcement.category.value if announcement.category else None,
        price=announcement.price,
        market_price=announcement.market_price,
        final_calculated_price=announcement.final_calculated_price,
        condition=announcement.condition.value if announcement.condition else None,
        status=announcement.status.value if announcement.status else None,
        description=announcement.description,
        custom_images=announcement.custom_images,
        location=announcement.location,
        page_count=announcement.page_count,
        publication_date=announcement.publication_date,
        views_count=announcement.views_count,
        created_at=announcement.created_at,
        updated_at=announcement.updated_at,
        book=book,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    )


# ============================================
# DELETE ANNOUNCEMENT
# ============================================
@router.delete("/announcements/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Delete an announcement (only by owner)"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not announcement:
        raise ResourceNotFoundError("Annonce", announcement_id)
    
    if announcement.user_id != user_id:
        raise ForbiddenError(
            "Vous n'êtes pas autorisé à supprimer cette annonce. "
            "Seul le propriétaire peut supprimer une annonce."
        )
    
    try:
        db.delete(announcement)
        db.commit()
        
        return {
            "success": True,
            "message": "Annonce supprimée avec succès",
            "data": {"id": announcement_id}
        }
    except Exception as e:
        db.rollback()
        error_logger.log_error(
            error_type="DatabaseError",
            message=f"Erreur lors de la suppression de l'annonce {announcement_id}",
            status_code=500,
            extra_data={"announcement_id": announcement_id, "user_id": user_id}
        )
        raise DatabaseError("Erreur lors de la suppression de l'annonce")
