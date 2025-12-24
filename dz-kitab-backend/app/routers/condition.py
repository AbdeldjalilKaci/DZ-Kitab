# app/routers/condition.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.book_condition import BookConditionScore
from app.models.book import Announcement
from app.schemas.condition import (
    BookConditionInput,
    BookConditionResponse,
    PriceSuggestionResponse,
    ConditionSummary,
    ScoreBreakdown
)
from app.middleware.auth import security
from app.services.jwt import verify_token
from app.models.user import User

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


@router.post("/evaluate/{announcement_id}", response_model=BookConditionResponse)
def evaluate_book_condition(
    announcement_id: int,
    condition_data: BookConditionInput,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Évaluer l'état du livre et calculer le prix final
    
    - Répond à 15 questions réparties en 5 catégories
    - Calcule automatiquement le score global (0-100%)
    - Calcule le prix final: market_price × (overall_score / 100)
    """
    # Vérifier que l'annonce existe et appartient à l'utilisateur
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annonce non trouvée"
        )
    
    if announcement.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à évaluer cette annonce"
        )
    
    # Vérifier si une évaluation existe déjà
    existing_score = db.query(BookConditionScore).filter(
        BookConditionScore.announcement_id == announcement_id
    ).first()
    
    if existing_score:
        # Mettre à jour l'évaluation existante
        condition_score = existing_score
    else:
        # Créer une nouvelle évaluation
        condition_score = BookConditionScore(announcement_id=announcement_id)
    
    # Page Score
    condition_score.page_no_missing = condition_data.page_score.no_missing
    condition_score.page_no_torn = condition_data.page_score.no_torn
    condition_score.page_clean = condition_data.page_score.clean
    
    # Binding Score
    condition_score.binding_no_loose = condition_data.binding_score.no_loose
    condition_score.binding_no_falling = condition_data.binding_score.no_falling
    condition_score.binding_stable = condition_data.binding_score.stable
    
    # Cover Score
    condition_score.cover_no_detachment = condition_data.cover_score.no_detachment
    condition_score.cover_clean = condition_data.cover_score.clean
    condition_score.cover_no_scratches = condition_data.cover_score.no_scratches
    
    # Damage Score
    condition_score.damage_no_burns = condition_data.damage_score.no_burns
    condition_score.damage_no_smell = condition_data.damage_score.no_smell
    condition_score.damage_no_insects = condition_data.damage_score.no_insects
    
    # Accessories Score
    condition_score.accessories_complete = condition_data.accessories_score.complete
    condition_score.accessories_content = condition_data.accessories_score.content
    condition_score.accessories_extras = condition_data.accessories_score.extras
    
    # Photos
    if condition_data.photo_urls:
        condition_score.has_photos = True
        condition_score.photo_urls = condition_data.photo_urls
    
    # Calculer tous les scores
    overall_score = condition_score.calculate_scores()
    
    # Utiliser le market_price de l'annonce ou celui fourni
    market_price = condition_data.market_price or announcement.market_price
    
    if market_price:
        # Calcul du prix final: market_price * (overall_score / 100)
        final_price = round(market_price * (overall_score / 100), 2)
        
        condition_score.base_price = market_price
        condition_score.suggested_price = final_price
        
        # Mettre à jour l'annonce avec le prix calculé
        announcement.market_price = market_price
        announcement.final_calculated_price = final_price
    
    # Sauvegarder
    if not existing_score:
        db.add(condition_score)
    
    db.commit()
    db.refresh(condition_score)
    db.refresh(announcement)
    
    # Calculer le multiplicateur pour la réponse
    multiplier = None
    if condition_score.base_price and condition_score.suggested_price:
        multiplier = round(condition_score.suggested_price / condition_score.base_price, 2)
    
    return BookConditionResponse(
        id=condition_score.id,
        announcement_id=condition_score.announcement_id,
        page_score=condition_score.page_score,
        binding_score=condition_score.binding_score,
        cover_score=condition_score.cover_score,
        damage_score=condition_score.damage_score,
        accessories_score=condition_score.accessories_score,
        overall_score=condition_score.overall_score,
        condition_label=condition_score.condition_label,
        market_price=condition_score.base_price,
        final_calculated_price=announcement.final_calculated_price,
        price_multiplier=multiplier,
        has_photos=condition_score.has_photos,
        photo_urls=condition_score.photo_urls,
        ai_analysis=condition_score.ai_analysis
    )


@router.get("/score/{announcement_id}", response_model=BookConditionResponse)
def get_condition_score(
    announcement_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupérer le score d'évaluation d'une annonce (public)
    """
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annonce non trouvée"
        )
    
    condition_score = db.query(BookConditionScore).filter(
        BookConditionScore.announcement_id == announcement_id
    ).first()
    
    if not condition_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune évaluation trouvée pour cette annonce"
        )
    
    multiplier = None
    if condition_score.base_price and condition_score.suggested_price:
        multiplier = round(condition_score.suggested_price / condition_score.base_price, 2)
    
    return BookConditionResponse(
        id=condition_score.id,
        announcement_id=condition_score.announcement_id,
        page_score=condition_score.page_score,
        binding_score=condition_score.binding_score,
        cover_score=condition_score.cover_score,
        damage_score=condition_score.damage_score,
        accessories_score=condition_score.accessories_score,
        overall_score=condition_score.overall_score,
        condition_label=condition_score.condition_label,
        market_price=condition_score.base_price,
        final_calculated_price=announcement.final_calculated_price,
        price_multiplier=multiplier,
        has_photos=condition_score.has_photos,
        photo_urls=condition_score.photo_urls,
        ai_analysis=condition_score.ai_analysis
    )


@router.get("/summary/{announcement_id}", response_model=ConditionSummary)
def get_condition_summary(
    announcement_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupérer un résumé visuel de l'état du livre avec recommandations
    """
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annonce non trouvée"
        )
    
    condition_score = db.query(BookConditionScore).filter(
        BookConditionScore.announcement_id == announcement_id
    ).first()
    
    if not condition_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune évaluation trouvée pour cette annonce"
        )
    
    # Créer le breakdown détaillé
    breakdown = {
        "pages": ScoreBreakdown(
            score=condition_score.page_score,
            percentage=condition_score.page_score,
            checks_passed=sum([
                condition_score.page_no_missing,
                condition_score.page_no_torn,
                condition_score.page_clean
            ]),
            total_checks=3
        ),
        "reliure": ScoreBreakdown(
            score=condition_score.binding_score,
            percentage=condition_score.binding_score,
            checks_passed=sum([
                condition_score.binding_no_loose,
                condition_score.binding_no_falling,
                condition_score.binding_stable
            ]),
            total_checks=3
        ),
        "couverture": ScoreBreakdown(
            score=condition_score.cover_score,
            percentage=condition_score.cover_score,
            checks_passed=sum([
                condition_score.cover_no_detachment,
                condition_score.cover_clean,
                condition_score.cover_no_scratches
            ]),
            total_checks=3
        ),
        "dégâts": ScoreBreakdown(
            score=condition_score.damage_score,
            percentage=condition_score.damage_score,
            checks_passed=sum([
                condition_score.damage_no_burns,
                condition_score.damage_no_smell,
                condition_score.damage_no_insects
            ]),
            total_checks=3
        ),
        "accessoires": ScoreBreakdown(
            score=condition_score.accessories_score,
            percentage=condition_score.accessories_score,
            checks_passed=sum([
                condition_score.accessories_complete,
                condition_score.accessories_content,
                condition_score.accessories_extras
            ]),
            total_checks=3
        )
    }
    
    # Générer des recommandations
    recommendations = []
    if condition_score.page_score < 80:
        recommendations.append("Les pages montrent des signes d'usure")
    if condition_score.binding_score < 80:
        recommendations.append("La reliure nécessite une attention")
    if condition_score.cover_score < 80:
        recommendations.append("La couverture présente des imperfections")
    if not condition_score.has_photos:
        recommendations.append("Ajoutez des photos pour augmenter vos chances de vente de 3x!")
    if condition_score.overall_score >= 90:
        recommendations.append("Excellent état! Ce livre se vendra rapidement")
    
    # Impact sur le prix
    if announcement.final_calculated_price and announcement.market_price:
        diff = announcement.market_price - announcement.final_calculated_price
        percentage = (diff / announcement.market_price) * 100
        if percentage > 0:
            price_impact = f"Prix réduit de {percentage:.0f}% en raison de l'état"
        else:
            price_impact = f"Prix à {abs(percentage):.0f}% du prix du marché"
    else:
        price_impact = "Prix basé sur l'état global"
    
    return ConditionSummary(
        overall_score=condition_score.overall_score,
        condition_label=condition_score.condition_label,
        breakdown=breakdown,
        recommendations=recommendations,
        price_impact=price_impact,
        final_calculated_price=announcement.final_calculated_price
    )


@router.post("/suggest-price/{announcement_id}", response_model=PriceSuggestionResponse)
def suggest_price(
    announcement_id: int,
    market_price: float,
    db: Session = Depends(get_db)
):
    """
    Obtenir une suggestion de prix basée sur l'évaluation existante
    Prix final = market_price × (overall_score / 100)
    """
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annonce non trouvée"
        )
    
    condition_score = db.query(BookConditionScore).filter(
        BookConditionScore.announcement_id == announcement_id
    ).first()
    
    if not condition_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune évaluation trouvée. Veuillez d'abord évaluer le livre."
        )
    
    # Calculer le prix final
    final_calculated_price = round(market_price * (condition_score.overall_score / 100), 2)
    multiplier = round(condition_score.overall_score / 100, 2)
    
    # Mettre à jour les prix
    condition_score.base_price = market_price
    condition_score.suggested_price = final_calculated_price
    announcement.market_price = market_price
    announcement.final_calculated_price = final_calculated_price
    
    db.commit()
    
    # Créer le breakdown du calcul
    price_breakdown = {
        "market_price": market_price,
        "condition_score_percentage": condition_score.overall_score,
        "multiplier": multiplier,
        "final_price": final_calculated_price,
        "reduction_amount": round(market_price - final_calculated_price, 2)
    }
    
    return PriceSuggestionResponse(
        market_price=market_price,
        overall_score=condition_score.overall_score,
        final_calculated_price=final_calculated_price,
        condition_label=condition_score.condition_label,
        price_breakdown=price_breakdown,
        message=f"Prix suggéré basé sur un état '{condition_score.condition_label}' (score: {condition_score.overall_score:.1f}%)"
    )
