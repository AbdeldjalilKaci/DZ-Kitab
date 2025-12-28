# app/routers/wishlist.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.wishlist import Wishlist
from app.models.book import Announcement
from app.schemas.wishlist import WishlistCreate, WishlistResponse, WishlistList
from app.middleware.auth import security
from app.services.jwt import verify_token
from app.models.user import User

router = APIRouter()

def get_current_user_id(token: str = Depends(security), db: Session = Depends(get_db)) -> int:
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
    return user.id

@router.post("/", response_model=WishlistResponse)
def add_to_wishlist(
    wishlist_data: WishlistCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    # Check if announcement exists
    announcement = db.query(Announcement).filter(Announcement.id == wishlist_data.announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Annonce non trouvée")
    
    # Check if already in wishlist
    existing = db.query(Wishlist).filter(
        Wishlist.user_id == user_id,
        Wishlist.announcement_id == wishlist_data.announcement_id
    ).first()
    if existing:
        return existing

    wishlist_item = Wishlist(user_id=user_id, announcement_id=wishlist_data.announcement_id)
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)
    return wishlist_item

@router.get("/", response_model=WishlistList)
def get_wishlist(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    items = db.query(Wishlist).filter(Wishlist.user_id == user_id).all()
    return {"total": len(items), "items": items}

@router.delete("/{announcement_id}")
def remove_from_wishlist(
    announcement_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    item = db.query(Wishlist).filter(
        Wishlist.user_id == user_id,
        Wishlist.announcement_id == announcement_id
    ).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item non trouvé dans la wishlist")
    
    db.delete(item)
    db.commit()
    return {"message": "Supprimé de la wishlist"}
