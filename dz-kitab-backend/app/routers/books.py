
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.book import Book, Announcement
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

router = APIRouter()


def get_current_user_id(token: str = Depends(security), db: Session = Depends(get_db)) -> int:
    """Get the current authenticated user ID from token"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return user.id


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
    
    This endpoint is used to auto-fill the book form when creating an announcement.
    The user enters the ISBN, and this endpoint returns all book details including cover image.
    """
    try:
        # Fetch book info from Google Books
        book_info = await fetch_book_by_isbn(isbn)
        
        if not book_info:
            return ISBNLookupResponse(
                found=False,
                message=f"Aucun livre trouvé pour l'ISBN: {isbn}. Vérifiez que l'ISBN est correct ou essayez un autre ISBN. Exemples d'ISBN valides : 9780439708180 (Harry Potter), 9782070612758 (Le Petit Prince)"
            )
        
        return ISBNLookupResponse(
            found=True,
            book_info=GoogleBookInfo(**book_info)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in ISBN lookup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la recherche du livre"
        )


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
    Create a new book announcement
    
    This endpoint:
    1. Fetches book info from Google Books API using the ISBN
    2. Creates or retrieves the book in the database
    3. Creates the announcement linked to that book and the current user
    """
    try:
        # 1. Fetch book info from Google Books
        book_info = await fetch_book_by_isbn(announcement_data.isbn)
        
        if not book_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Aucun livre trouvé pour l'ISBN: {announcement_data.isbn}"
            )
        
        # 2. Check if book already exists in database
        book = db.query(Book).filter(Book.isbn == book_info["isbn"]).first()
        
        if not book:
            # Create new book entry
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
        
        # 3. Create announcement
        custom_images_str = None
        if announcement_data.custom_images:
            custom_images_str = ",".join(announcement_data.custom_images)
        
        announcement = Announcement(
            book_id=book.id,
            user_id=user_id,
            price=announcement_data.price,
            condition=announcement_data.condition.value,
            description=announcement_data.description,
            location=announcement_data.location,
            custom_images=custom_images_str
        )
        
        db.add(announcement)
        db.commit()
        db.refresh(announcement)
        
        # 4. Prepare response with nested data
        user = db.query(User).filter(User.id == user_id).first()
        
        return AnnouncementResponse(
            id=announcement.id,
            book_id=announcement.book_id,
            user_id=announcement.user_id,
            price=announcement.price,
            condition=announcement.condition.value,
            status=announcement.status.value,
            description=announcement.description,
            custom_images=announcement.custom_images,
            location=announcement.location,
            views_count=announcement.views_count,
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
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating announcement: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de l'annonce: {str(e)}"
        )


# ============================================
# GET ANNOUNCEMENTS
# ============================================

@router.get("/announcements", response_model=AnnouncementListResponse)
def get_announcements(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    condition: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of all active announcements (public endpoint)
    
    Optional filters:
    - status: Filter by announcement status
    - condition: Filter by book condition
    """
    try:
        query = db.query(Announcement)
        
        # Apply filters
        if status:
            query = query.filter(Announcement.status == status)
        if condition:
            query = query.filter(Announcement.condition == condition)
        
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
                    price=ann.price,
                    condition=ann.condition.value,
                    status=ann.status.value,
                    description=ann.description,
                    custom_images=ann.custom_images,
                    location=ann.location,
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
        print(f"❌ Error fetching announcements: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des annonces"
        )


@router.get("/announcements/{announcement_id}", response_model=AnnouncementResponse)
def get_announcement(announcement_id: int, db: Session = Depends(get_db)):
    """Get a specific announcement by ID"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annonce non trouvée"
        )
    
    # Increment view count
    announcement.views_count += 1
    db.commit()
    
    book = db.query(Book).filter(Book.id == announcement.book_id).first()
    user = db.query(User).filter(User.id == announcement.user_id).first()
    
    return AnnouncementResponse(
        id=announcement.id,
        book_id=announcement.book_id,
        user_id=announcement.user_id,
        price=announcement.price,
        condition=announcement.condition.value,
        status=announcement.status.value,
        description=announcement.description,
        custom_images=announcement.custom_images,
        location=announcement.location,
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
                price=ann.price,
                condition=ann.condition.value,
                status=ann.status.value,
                description=ann.description,
                custom_images=ann.custom_images,
                location=ann.location,
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annonce non trouvée"
        )
    
    # Check ownership
    if announcement.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à modifier cette annonce"
        )
    
    # Update fields
    if update_data.price is not None:
        announcement.price = update_data.price
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
    
    db.commit()
    db.refresh(announcement)
    
    book = db.query(Book).filter(Book.id == announcement.book_id).first()
    user = db.query(User).filter(User.id == announcement.user_id).first()
    
    return AnnouncementResponse(
        id=announcement.id,
        book_id=announcement.book_id,
        user_id=announcement.user_id,
        price=announcement.price,
        condition=announcement.condition.value,
        status=announcement.status.value,
        description=announcement.description,
        custom_images=announcement.custom_images,
        location=announcement.location,
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
    """Delete an announcement (only by the owner)"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annonce non trouvée"
        )
    
    # Check ownership
    if announcement.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à supprimer cette annonce"
        )
    
    db.delete(announcement)
    db.commit()
    
    return {
        "message": "Annonce supprimée avec succès",
        "announcement_id": announcement_id
    }