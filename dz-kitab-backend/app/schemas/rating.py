from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RatingCreate(BaseModel):
    announcement_id: int
    rating: int = Field(..., ge=1, le=5, description="Note globale (1-5 étoiles)")
    comment: Optional[str] = Field(None, max_length=1000)
    communication_rating: Optional[int] = Field(None, ge=1, le=5)
    condition_accuracy_rating: Optional[int] = Field(None, ge=1, le=5)
    delivery_speed_rating: Optional[int] = Field(None, ge=1, le=5)

class RatingUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)
    communication_rating: Optional[int] = Field(None, ge=1, le=5)
    condition_accuracy_rating: Optional[int] = Field(None, ge=1, le=5)
    delivery_speed_rating: Optional[int] = Field(None, ge=1, le=5)

class RatingResponse(BaseModel):
    id: int
    buyer_id: int
    seller_id: int
    announcement_id: int
    rating: int
    comment: Optional[str] = None
    communication_rating: Optional[int] = None
    condition_accuracy_rating: Optional[int] = None
    delivery_speed_rating: Optional[int] = None
    created_at: datetime
    buyer_username: str
    seller_username: str

    class Config:
        from_attributes = True

class RatingListResponse(BaseModel):
    total: int
    ratings: List[RatingResponse]

class SellerStatsResponse(BaseModel):
    user_id: int
    total_ratings: int
    average_rating: float
    avg_communication: float
    avg_condition_accuracy: float
    avg_delivery_speed: float
    rating_5_count: int
    rating_4_count: int
    rating_3_count: int
    rating_2_count: int
    rating_1_count: int
    is_top_seller: bool
    total_sales: int

    class Config:
        from_attributes = True
