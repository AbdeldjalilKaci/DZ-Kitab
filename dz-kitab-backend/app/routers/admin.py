# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.book import Announcement, Book
from app.models.rating import Rating, SellerStats
from app.middleware.auth import security
from app.services.jwt import verify_token

router = APIRouter()

def get_current_admin(token: str = Depends(security), db: Session = Depends(get_db)) -> User:
    """
    ✅ CORRECTION: Verify the current user is an admin using is_admin field
    """
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
    
    # Check if user is admin (you may need to add is_admin field to User model)
    # For now, we'll check if username contains 'admin' or email contains 'admin'
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs. Contactez un administrateur pour obtenir les privilèges."
        )
    
    return user

# ============================================
# DASHBOARD STATISTICS
# ============================================

@router.get("/stats/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get overall dashboard statistics"""
    try:
        # User statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        blocked_users = db.query(User).filter(User.is_active == False).count()
        
        # Count admins (you may need to adjust this based on your admin logic)
        admins = db.query(User).filter(
            (User.email.contains('admin')) | (User.username.contains('admin'))
        ).count()
        
        # Announcement statistics
        total_announcements = db.query(Announcement).count()
        active_announcements = db.query(Announcement).filter(
            Announcement.status == "Active"
        ).count()
        sold_announcements = db.query(Announcement).filter(
            Announcement.status == "Vendu"
        ).count()
        reserved_announcements = db.query(Announcement).filter(
            Announcement.status == "Réservé"
        ).count()
        
        # Rating statistics
        total_ratings = db.query(Rating).count()
        avg_rating = db.query(func.avg(Rating.rating)).scalar() or 0.0
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_users_week = db.query(User).filter(User.created_at >= week_ago).count()
        new_announcements_week = db.query(Announcement).filter(
            Announcement.created_at >= week_ago
        ).count()
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "blocked": blocked_users,
                "admins": admins,
                "new_this_week": new_users_week
            },
            "announcements": {
                "total": total_announcements,
                "active": active_announcements,
                "sold": sold_announcements,
                "reserved": reserved_announcements,
                "new_this_week": new_announcements_week
            },
            "ratings": {
                "total": total_ratings,
                "average": round(avg_rating, 2)
            }
        }
        
    except Exception as e:
        print(f"❌ Error fetching dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des statistiques"
        )

@router.get("/stats/popular-books")
def get_popular_books(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get most popular books by announcement count"""
    try:
        popular_books = db.query(
            Book.id,
            Book.title,
            Book.categories,
            func.count(Announcement.id).label('listing_count')
        ).join(
            Announcement, Book.id == Announcement.book_id
        ).group_by(
            Book.id, Book.title, Book.categories
        ).order_by(
            func.count(Announcement.id).desc()
        ).limit(limit).all()
        
        result = []
        for book in popular_books:
            total_announcements = db.query(Announcement).count()
            percentage = (book.listing_count / total_announcements * 100) if total_announcements > 0 else 0
            
            result.append({
                "id": book.id,
                "title": book.title,
                "category": book.categories or "Autre",
                "listings": book.listing_count,
                "percentage": round(percentage, 1)
            })
        
        return {"books": result}
        
    except Exception as e:
        print(f"❌ Error fetching popular books: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des livres populaires"
        )

@router.get("/stats/sales-by-category")
def get_sales_by_category(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get sales distribution by category"""
    try:
        # Get sold announcements by category
        sales_by_category = db.query(
            Announcement.category,
            func.count(Announcement.id).label('count')
        ).filter(
            Announcement.status == "Vendu"
        ).group_by(
            Announcement.category
        ).all()
        
        total_sales = sum(sale.count for sale in sales_by_category)
        
        result = []
        for sale in sales_by_category:
            percentage = (sale.count / total_sales * 100) if total_sales > 0 else 0
            result.append({
                "category": sale.category,
                "count": sale.count,
                "percentage": round(percentage, 1)
            })
        
        return {
            "total_sales": total_sales,
            "categories": sorted(result, key=lambda x: x['count'], reverse=True)
        }
        
    except Exception as e:
        print(f"❌ Error fetching sales by category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des ventes par catégorie"
        )

# ============================================
# USER MANAGEMENT
# ============================================

@router.get("/users")
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get all users with filters"""
    try:
        query = db.query(User)
        
        # Apply filters
        if search:
            query = query.filter(
                (User.username.contains(search)) | 
                (User.email.contains(search)) |
                (User.first_name.contains(search)) |
                (User.last_name.contains(search))
            )
        
        if status:
            if status.lower() == 'active':
                query = query.filter(User.is_active == True)
            elif status.lower() == 'blocked':
                query = query.filter(User.is_active == False)
        
        if role:
            if role.lower() == 'admin':
                query = query.filter(
                    (User.email.contains('admin')) | (User.username.contains('admin'))
                )
            elif role.lower() == 'user':
                query = query.filter(
                    ~User.email.contains('admin'),
                    ~User.username.contains('admin')
                )
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
        result = []
        for user in users:
            # Determine role
            is_admin = 'admin' in user.email.lower() or 'admin' in user.username.lower()
            
            result.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "university": user.university.value if user.university else None,
                "phone_number": user.phone_number,
                "is_active": user.is_active,
                "role": "Admin" if is_admin else "User",
                "created_at": user.created_at.isoformat(),
                "announcements_count": db.query(Announcement).filter(
                    Announcement.user_id == user.id
                ).count()
            })
        
        return {
            "total": total,
            "users": result
        }
        
    except Exception as e:
        print(f"❌ Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des utilisateurs"
        )

@router.put("/users/{user_id}/block")
def block_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Block a user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        if user.id == admin.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vous ne pouvez pas bloquer votre propre compte"
            )
        
        user.is_active = False
        db.commit()
        
        return {
            "message": f"Utilisateur {user.username} bloqué avec succès",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error blocking user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du blocage de l'utilisateur"
        )

@router.put("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Activate a blocked user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        user.is_active = True
        db.commit()
        
        return {
            "message": f"Utilisateur {user.username} activé avec succès",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error activating user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'activation de l'utilisateur"
        )

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Delete a user (soft delete by blocking)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        if user.id == admin.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vous ne pouvez pas supprimer votre propre compte"
            )
        
        # Soft delete - just block the user
        user.is_active = False
        db.commit()
        
        return {
            "message": f"Utilisateur {user.username} supprimé avec succès",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression de l'utilisateur"
        )

# ============================================
# ANNOUNCEMENT MANAGEMENT
# ============================================

@router.get("/announcements")
def get_all_announcements(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get all announcements with filters"""
    try:
        query = db.query(Announcement)
        
        if search:
            # Join with Book table to search by title
            query = query.join(Book).filter(
                Book.title.contains(search)
            )
        
        if status:
            query = query.filter(Announcement.status == status)
        
        if category:
            query = query.filter(Announcement.category == category)
        
        total = query.count()
        announcements = query.offset(skip).limit(limit).all()
        
        result = []
        for ann in announcements:
            book = db.query(Book).filter(Book.id == ann.book_id).first()
            user = db.query(User).filter(User.id == ann.user_id).first()
            
            result.append({
                "id": ann.id,
                "title": book.title if book else "Unknown",
                "category": ann.category,
                "price": ann.price,
                "status": ann.status,
                "seller": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                } if user else None,
                "views_count": ann.views_count,
                "created_at": ann.created_at.isoformat(),
                "cover_image": book.cover_image_url if book else None
            })
        
        return {
            "total": total,
            "announcements": result
        }
        
    except Exception as e:
        print(f"❌ Error fetching announcements: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des annonces"
        )

@router.delete("/announcements/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Delete an announcement"""
    try:
        announcement = db.query(Announcement).filter(
            Announcement.id == announcement_id
        ).first()
        
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Annonce non trouvée"
            )
        
        db.delete(announcement)
        db.commit()
        
        return {
            "message": "Annonce supprimée avec succès",
            "announcement_id": announcement_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting announcement: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression de l'annonce"
        )

@router.get("/test")
def test_admin():
    """Test endpoint"""
    return {
        "message": "Admin router is working!",
        "endpoints": [
            "GET /admin/stats/dashboard",
            "GET /admin/stats/popular-books",
            "GET /admin/stats/sales-by-category",
            "GET /admin/users",
            "PUT /admin/users/{id}/block",
            "PUT /admin/users/{id}/activate",
            "DELETE /admin/users/{id}",
            "GET /admin/announcements",
            "DELETE /admin/announcements/{id}"
        ]
    }
