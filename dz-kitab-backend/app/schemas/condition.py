# app/schemas/condition.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class PageScore(BaseModel):
    no_missing: bool = Field(..., description="Aucune page manquante")
    no_torn: bool = Field(..., description="Pas de pages déchirées")
    clean: bool = Field(..., description="Pages propres")

class BindingScore(BaseModel):
    no_loose: bool = Field(..., description="Pas de fil/colle visible")
    no_falling: bool = Field(..., description="Pages ne tombent pas")
    stable: bool = Field(..., description="Reliure stable")

class CoverScore(BaseModel):
    no_detachment: bool = Field(..., description="Pas de détachement")
    clean: bool = Field(..., description="Couverture propre")
    no_scratches: bool = Field(..., description="Pas de rayures")

class DamageScore(BaseModel):
    no_burns: bool = Field(..., description="Pas de brûlures/taches")
    no_smell: bool = Field(..., description="Pas d'odeur forte")
    no_insects: bool = Field(..., description="Pas de traces d'insectes")

class AccessoriesScore(BaseModel):
    complete: bool = Field(..., description="Accessoires complets")
    content: bool = Field(..., description="Contenu interne complet")
    extras: bool = Field(..., description="Extras présents")

class BookConditionInput(BaseModel):
    page_score: PageScore
    binding_score: BindingScore
    cover_score: CoverScore
    damage_score: DamageScore
    accessories_score: AccessoriesScore
    base_price: Optional[float] = None
    photo_urls: Optional[List[str]] = None

class BookConditionResponse(BaseModel):
    id: int
    announcement_id: int
    page_score: float
    binding_score: float
    cover_score: float
    damage_score: float
    accessories_score: float
    overall_score: float
    condition_label: str
    base_price: Optional[float] = None
    suggested_price: Optional[float] = None
    price_multiplier: Optional[float] = None
    has_photos: bool
    photo_urls: Optional[List[str]] = None
    ai_analysis: Optional[Dict] = None

    class Config:
        from_attributes = True

class ScoreBreakdown(BaseModel):
    score: float
    percentage: float
    checks_passed: int
    total_checks: int

class ConditionSummary(BaseModel):
    overall_score: float
    condition_label: str
    breakdown: Dict[str, ScoreBreakdown]
    recommendations: List[str]
    price_impact: str

class PriceSuggestionResponse(BaseModel):
    base_price: float
    suggested_price: float
    multiplier: float
    overall_score: float
    condition_label: str
    message: str