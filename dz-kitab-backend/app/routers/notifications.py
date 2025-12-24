# app/routers/notifications.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.notification import Notification, NotificationPreference, NotificationType
from app.models.user import User
from app.middleware.auth import security
from app.services.jwt import verify_token

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
# GET NOTIFICATIONS
# ============================================

@router.get("/", status_code=status.HTTP_200_OK)
def get_my_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get all notifications for the current user
    
    - **skip**: Number of notifications to skip (pagination)
    - **limit**: Maximum number of notifications to return
    - **unread_only**: If true, return only unread notifications
    """
    try:
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        total = query.count()
        notifications = query.order_by(
            Notification.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "unread_count": db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            ).count(),
            "notifications": [
                {
                    "id": n.id,
                    "type": n.type.value,
                    "title": n.title,
                    "message": n.message,
                    "related_user_id": n.related_user_id,
                    "related_announcement_id": n.related_announcement_id,
                    "related_rating_id": n.related_rating_id,
                    "action_url": n.action_url,
                    "is_read": n.is_read,
                    "created_at": n.created_at.isoformat(),
                    "read_at": n.read_at.isoformat() if n.read_at else None
                }
                for n in notifications
            ]
        }
        
    except Exception as e:
        print(f"❌ Error fetching notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des notifications"
        )

@router.get("/unread-count", status_code=status.HTTP_200_OK)
def get_unread_count(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get the count of unread notifications"""
    try:
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
        
        return {"unread_count": count}
        
    except Exception as e:
        print(f"❌ Error getting unread count: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du comptage des notifications"
        )

# ============================================
# MARK AS READ
# ============================================

@router.put("/{notification_id}/read", status_code=status.HTTP_200_OK)
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Mark a specific notification as read"""
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification non trouvée"
            )
        
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.commit()
        
        return {
            "message": "Notification marquée comme lue",
            "notification_id": notification_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error marking notification as read: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour"
        )

@router.put("/read-all", status_code=status.HTTP_200_OK)
def mark_all_as_read(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Mark all notifications as read for the current user"""
    try:
        updated = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        
        db.commit()
        
        return {
            "message": "Toutes les notifications ont été marquées comme lues",
            "count": updated
        }
        
    except Exception as e:
        print(f"❌ Error marking all as read: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour"
        )

# ============================================
# DELETE NOTIFICATIONS
# ============================================

@router.delete("/{notification_id}", status_code=status.HTTP_200_OK)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Delete a specific notification"""
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification non trouvée"
            )
        
        db.delete(notification)
        db.commit()
        
        return {
            "message": "Notification supprimée",
            "notification_id": notification_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting notification: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression"
        )

@router.delete("/delete-all", status_code=status.HTTP_200_OK)
def delete_all_read_notifications(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Delete all read notifications for the current user"""
    try:
        deleted = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == True
        ).delete()
        
        db.commit()
        
        return {
            "message": "Notifications lues supprimées",
            "count": deleted
        }
        
    except Exception as e:
        print(f"❌ Error deleting notifications: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression"
        )

# ============================================
# NOTIFICATION PREFERENCES
# ============================================

@router.get("/preferences", status_code=status.HTTP_200_OK)
def get_notification_preferences(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get notification preferences for the current user"""
    try:
        prefs = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
        
        if not prefs:
            # Create default preferences
            prefs = NotificationPreference(user_id=user_id)
            db.add(prefs)
            db.commit()
            db.refresh(prefs)
        
        return {
            "email_new_rating": prefs.email_new_rating,
            "email_rating_reply": prefs.email_rating_reply,
            "email_announcement_sold": prefs.email_announcement_sold,
            "email_low_rating_alert": prefs.email_low_rating_alert,
            "email_account_suspended": prefs.email_account_suspended,
            "email_message_received": prefs.email_message_received,
            "app_notifications_enabled": prefs.app_notifications_enabled
        }
        
    except Exception as e:
        print(f"❌ Error getting preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des préférences"
        )

@router.put("/preferences", status_code=status.HTTP_200_OK)
def update_notification_preferences(
    preferences: dict,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Update notification preferences"""
    try:
        prefs = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
        
        if not prefs:
            prefs = NotificationPreference(user_id=user_id)
            db.add(prefs)
        
        # Update preferences
        if "email_new_rating" in preferences:
            prefs.email_new_rating = preferences["email_new_rating"]
        if "email_rating_reply" in preferences:
            prefs.email_rating_reply = preferences["email_rating_reply"]
        if "email_announcement_sold" in preferences:
            prefs.email_announcement_sold = preferences["email_announcement_sold"]
        if "email_low_rating_alert" in preferences:
            prefs.email_low_rating_alert = preferences["email_low_rating_alert"]
        if "email_account_suspended" in preferences:
            prefs.email_account_suspended = preferences["email_account_suspended"]
        if "email_message_received" in preferences:
            prefs.email_message_received = preferences["email_message_received"]
        if "app_notifications_enabled" in preferences:
            prefs.app_notifications_enabled = preferences["app_notifications_enabled"]
        
        db.commit()
        
        return {
            "message": "Préférences mises à jour",
            "preferences": {
                "email_new_rating": prefs.email_new_rating,
                "email_rating_reply": prefs.email_rating_reply,
                "email_announcement_sold": prefs.email_announcement_sold,
                "email_low_rating_alert": prefs.email_low_rating_alert,
                "email_account_suspended": prefs.email_account_suspended,
                "email_message_received": prefs.email_message_received,
                "app_notifications_enabled": prefs.app_notifications_enabled
            }
        }
        
    except Exception as e:
        print(f"❌ Error updating preferences: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour"
        )

@router.get("/test")
def test_notifications():
    """Test endpoint"""
    return {
        "message": "Notifications router is working!",
        "endpoints": [
            "GET /notifications/",
            "GET /notifications/unread-count",
            "PUT /notifications/{id}/read",
            "PUT /notifications/read-all",
            "DELETE /notifications/{id}",
            "DELETE /notifications/delete-all",
            "GET /notifications/preferences",
            "PUT /notifications/preferences"
        ]
    }
