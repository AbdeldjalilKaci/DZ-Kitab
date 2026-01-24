# app/routers/dashboard.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.book import Announcement, AnnouncementStatusEnum
from app.models.rating import Rating, SellerStats
from app.models.notification import Notification
from app.models.wishlist import Wishlist
from app.middleware.auth import security
from app.services.jwt import verify_token

router = APIRouter()

def get_current_user(token: str = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user"""
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
    
    return user

# ============================================
# DASHBOARD OVERVIEW
# ============================================

@router.get("/overview")
def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📊 Get user dashboard overview with key statistics
    
    Returns:
    - Total listings (by status)
    - Books sold
    - Purchase requests received
    - Listings for sale
    - Messages count
    - Average rating
    """
    try:
        user_id = current_user.id
        
        # 1. Announcements statistics
        total_announcements = db.query(Announcement).filter(
            Announcement.user_id == user_id
        ).count()
        
        active_announcements = db.query(Announcement).filter(
            Announcement.user_id == user_id,
            Announcement.status == AnnouncementStatusEnum.ACTIVE
        ).count()
        
        sold_announcements = db.query(Announcement).filter(
            Announcement.user_id == user_id,
            Announcement.status == AnnouncementStatusEnum.VENDU
        ).count()
        
        reserved_announcements = db.query(Announcement).filter(
            Announcement.user_id == user_id,
            Announcement.status == AnnouncementStatusEnum.RESERVE
        ).count()
        
        # 2. Ratings statistics
        seller_stats = db.query(SellerStats).filter(
            SellerStats.user_id == user_id
        ).first()
        
        avg_rating = seller_stats.average_rating if seller_stats else 0.0
        total_ratings = seller_stats.total_ratings if seller_stats else 0
        
        # 3. Notifications (unread messages simulation)
        unread_notifications = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
        
        # 4. Wishlist count
        wishlist_count = db.query(Wishlist).filter(
            Wishlist.user_id == user_id
        ).count()
        
        # 5. Purchase requests (ratings given by user = purchases made)
        purchase_requests = db.query(Rating).filter(
            Rating.buyer_id == user_id
        ).count()
        
        return {
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "is_active": current_user.is_active
            },
            "stats": {
                "total_listings": total_announcements,
                "books_sold": sold_announcements,
                "purchase_requests": purchase_requests,
                "listings_for_sale": active_announcements,
                "reserved_listings": reserved_announcements,
                "unread_messages": unread_notifications,
                "wishlist_count": wishlist_count
            },
            "seller_stats": {
                "average_rating": round(avg_rating, 1),
                "total_ratings": total_ratings,
                "is_top_seller": seller_stats.is_top_seller if seller_stats else False
            }
        }
        
    except Exception as e:
        print(f"❌ Error fetching dashboard overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des statistiques"
        )

# ============================================
# SALES OVERVIEW (Monthly Chart Data)
# ============================================

@router.get("/sales-overview")
def get_sales_overview(
    months: int = Query(12, ge=1, le=24, description="Number of months to show"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📈 Get sales overview for the last N months
    
    Returns monthly data for chart visualization
    """
    try:
        user_id = current_user.id
        
        # Calculate start date
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 30)
        
        # Get sold announcements grouped by month
        sold_by_month = db.query(
            func.date_trunc('month', Announcement.updated_at).label('month'),
            func.count(Announcement.id).label('count')
        ).filter(
            Announcement.user_id == user_id,
            Announcement.status == AnnouncementStatusEnum.VENDU,
            Announcement.updated_at >= start_date
        ).group_by(
            func.date_trunc('month', Announcement.updated_at)
        ).order_by('month').all()
        
        # Format data for chart
        monthly_data = []
        month_names = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]
        
        for month_data in sold_by_month:
            month_date = month_data.month
            monthly_data.append({
                "month": month_names[month_date.month - 1],
                "year": month_date.year,
                "sales": month_data.count,
                "label": f"{month_names[month_date.month - 1]} {month_date.year}"
            })
        
        # Fill missing months with 0
        all_months = []
        current_date = start_date
        while current_date <= end_date:
            month_label = month_names[current_date.month - 1]
            
            # Check if data exists for this month
            existing = next(
                (m for m in monthly_data 
                 if m["month"] == month_label and m["year"] == current_date.year),
                None
            )
            
            if existing:
                all_months.append(existing)
            else:
                all_months.append({
                    "month": month_label,
                    "year": current_date.year,
                    "sales": 0,
                    "label": f"{month_label} {current_date.year}"
                })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "months": months
            },
            "total_sales": sum(m["sales"] for m in all_months),
            "data": all_months[-12:]  # Return last 12 months max for chart
        }
        
    except Exception as e:
        print(f"❌ Error fetching sales overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des ventes"
        )

# ============================================
# MOST REQUESTED BOOKS (User's Popular Listings)
# ============================================

@router.get("/popular-listings")
def get_popular_listings(
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📚 Get user's most popular listings by views
    
    Returns top N announcements sorted by views_count
    """
    try:
        from app.models.book import Book
        
        popular_listings = db.query(
            Announcement,
            Book
        ).join(
            Book, Book.id == Announcement.book_id
        ).filter(
            Announcement.user_id == current_user.id
        ).order_by(
            Announcement.views_count.desc()
        ).limit(limit).all()
        
        # Calculate total views for percentage
        total_views = db.query(
            func.sum(Announcement.views_count)
        ).filter(
            Announcement.user_id == current_user.id
        ).scalar() or 1  # Avoid division by zero
        
        result = []
        for announcement, book in popular_listings:
            percentage = (announcement.views_count / total_views * 100) if total_views > 0 else 0
            
            result.append({
                "id": announcement.id,
                "title": book.title,
                "cover_image": book.cover_image_url,
                "views": announcement.views_count,
                "percentage": round(percentage, 1),
                "price": announcement.price,
                "status": announcement.status.value,
                "category": announcement.category.value if hasattr(announcement.category, 'value') else announcement.category
            })
        
        return {
            "total_views": int(total_views),
            "listings": result
        }
        
    except Exception as e:
        print(f"❌ Error fetching popular listings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des annonces populaires"
        )

# ============================================
# RECENT ACTIVITY
# ============================================

@router.get("/recent-activity")
def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🕐 Get recent activity (notifications, ratings, sales)
    """
    try:
        activities = []
        
        # 1. Recent notifications
        recent_notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id
        ).order_by(Notification.created_at.desc()).limit(limit).all()
        
        for notif in recent_notifications:
            activities.append({
                "type": "notification",
                "title": notif.title,
                "message": notif.message,
                "timestamp": notif.created_at.isoformat(),
                "is_read": notif.is_read,
                "action_url": notif.action_url
            })
        
        # 2. Recent ratings received
        recent_ratings = db.query(Rating).filter(
            Rating.seller_id == current_user.id
        ).order_by(Rating.created_at.desc()).limit(5).all()
        
        for rating in recent_ratings:
            buyer = db.query(User).filter(User.id == rating.buyer_id).first()
            activities.append({
                "type": "rating",
                "title": f"Nouvelle note de {buyer.username if buyer else 'Utilisateur'}",
                "message": f"{rating.rating} étoiles",
                "timestamp": rating.created_at.isoformat(),
                "rating_value": rating.rating
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "total": len(activities),
            "activities": activities[:limit]
        }
        
    except Exception as e:
        print(f"❌ Error fetching recent activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de l'activité"
        )

# ============================================
# PROFILE SETTINGS (for the Profile Settings section in dashboard)
# ============================================

@router.get("/profile")
def get_profile_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    👤 Get user profile information for settings
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "university": current_user.university.value if current_user.university else None,
        "phone_number": current_user.phone_number,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat()
    }

@router.put("/profile")
def update_profile_settings(
    profile_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ✏️ Update user profile information
    """
    try:
        # Update allowed fields
        if "first_name" in profile_data:
            current_user.first_name = profile_data["first_name"]
        if "last_name" in profile_data:
            current_user.last_name = profile_data["last_name"]
        if "phone_number" in profile_data:
            current_user.phone_number = profile_data["phone_number"]
        
        db.commit()
        db.refresh(current_user)
        
        return {
            "message": "Profil mis à jour avec succès",
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "phone_number": current_user.phone_number
            }
        }
        
    except Exception as e:
        print(f"❌ Error updating profile: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du profil"
        )

# ============================================
# TEST ENDPOINT
# ============================================

@router.get("/test")
def test_dashboard():
    """Test endpoint to verify dashboard router is working"""
    return {
        "message": "✅ Dashboard router is working!",
        "endpoints": [
            "GET /api/dashboard/overview - Main dashboard stats",
            "GET /api/dashboard/sales-overview - Monthly sales chart",
            "GET /api/dashboard/popular-listings - Most viewed listings",
            "GET /api/dashboard/recent-activity - Recent notifications/ratings",
            "GET /api/dashboard/profile - User profile info",
            "PUT /api/dashboard/profile - Update profile"
        ]
    }
