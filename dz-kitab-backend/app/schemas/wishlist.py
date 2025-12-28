# app/schemas/wishlist.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .book import AnnouncementResponse

class WishlistBase(BaseModel):
    announcement_id: int

class WishlistCreate(WishlistBase):
    pass

class WishlistResponse(BaseModel):
    id: int
    user_id: int
    announcement_id: int
    created_at: datetime
    announcement: Optional[AnnouncementResponse] = None

    class Config:
        from_attributes = True

class WishlistList(BaseModel):
    total: int
    items: List[WishlistResponse]
