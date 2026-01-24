# app/services/curriculum_service.py

from sqlalchemy.orm import Session
from app.models.curriculum import Curriculum, RecommendedBook, BookCurriculumMatch
from app.models.book import Book
from typing import List, Dict, Optional
from difflib import SequenceMatcher


def normalize_string(s: str) -> str:
    """Normaliser une chaîne pour la comparaison"""
    if not s:
        return ""
    return s.lower().strip().replace("-", " ").replace("'", " ")


def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculer la similarité entre deux chaînes (0.0 à 1.0)
    """
    return SequenceMatcher(None, normalize_string(str1), normalize_string(str2)).ratio()


def match_book_to_recommendations(db: Session, book: Book) -> List[BookCurriculumMatch]:
    """
    Trouver si un livre correspond à des livres recommandés
    
    Returns:
        Liste des correspondances trouvées
    """
    matches = []
    
    # 1. Match par ISBN (exact)
    if book.isbn:
        recommended = db.query(RecommendedBook).filter(
            RecommendedBook.isbn == book.isbn
        ).all()
        
        for rec in recommended:
            match = BookCurriculumMatch(
                book_id=book.id,
                recommended_book_id=rec.id,
                match_score=100,
                match_method="isbn"
            )
            matches.append(match)
    
    # 2. Match par titre exact
    recommended = db.query(RecommendedBook).filter(
        RecommendedBook.title.ilike(f"%{book.title}%")
    ).all()
    
    for rec in recommended:
        # Vérifier si ce match n'existe pas déjà
        if not any(m.recommended_book_id == rec.id for m in matches):
            similarity = calculate_similarity(book.title, rec.title)
            
            if similarity >= 0.85:  # 85% de similarité
                match = BookCurriculumMatch(
                    book_id=book.id,
                    recommended_book_id=rec.id,
                    match_score=int(similarity * 100),
                    match_method="title_exact"
                )
                matches.append(match)
    
    # 3. Match fuzzy (titre similaire)
    if not matches:
        all_recommended = db.query(RecommendedBook).all()
        
        for rec in all_recommended:
            similarity = calculate_similarity(book.title, rec.title)
            
            if similarity >= 0.7:  # 70% de similarité
                match = BookCurriculumMatch(
                    book_id=book.id,
                    recommended_book_id=rec.id,
                    match_score=int(similarity * 100),
                    match_method="title_fuzzy"
                )
                matches.append(match)
    
    return matches


def get_book_curriculum_badges(db: Session, book_id: int) -> List[Dict]:
    """
    Obtenir les badges de curriculum pour un livre
    
    Returns:
        Liste de dictionnaires avec les informations des cursus
    """
    badges = []
    
    # Récupérer les matches pour ce livre
    matches = db.query(BookCurriculumMatch).filter(
        BookCurriculumMatch.book_id == book_id,
        BookCurriculumMatch.match_score >= 70  # Seuil minimum
    ).all()
    
    for match in matches:
        recommended_book = db.query(RecommendedBook).filter(
            RecommendedBook.id == match.recommended_book_id
        ).first()
        
        if recommended_book:
            # Récupérer tous les cursus pour ce livre recommandé
            for curriculum in recommended_book.curriculums:
                badges.append({
                    "curriculum_id": curriculum.id,
                    "curriculum_name": curriculum.name,
                    "university": curriculum.university,
                    "field": curriculum.field,
                    "year": curriculum.year,
                    "match_score": match.match_score,
                    "match_method": match.match_method,
                    "badge_text": f"Recommandé en {curriculum.name}"
                })
    
    # Retourner les badges uniques triés par score
    unique_badges = []
    seen = set()
    
    for badge in sorted(badges, key=lambda x: x["match_score"], reverse=True):
        key = (badge["curriculum_id"], badge["curriculum_name"])
        if key not in seen:
            seen.add(key)
            unique_badges.append(badge)
    
    return unique_badges


def auto_match_all_books(db: Session):
    """
    Matcher automatiquement tous les livres existants avec les recommandations
    À exécuter après le scraping ou périodiquement
    """
    print("\n🔍 Matching automatique des livres...")
    
    books = db.query(Book).all()
    total_matches = 0
    
    for book in books:
        # Vérifier si des matches existent déjà
        existing = db.query(BookCurriculumMatch).filter(
            BookCurriculumMatch.book_id == book.id
        ).count()
        
        if existing > 0:
            continue  # Déjà matché
        
        # Trouver les correspondances
        matches = match_book_to_recommendations(db, book)
        
        if matches:
            for match in matches:
                db.add(match)
                total_matches += 1
            
            print(f"✅ {book.title}: {len(matches)} correspondance(s)")
    
    db.commit()
    print(f"\n✅ {total_matches} correspondances créées\n")


def search_books_by_curriculum(db: Session, curriculum_id: int) -> List[Book]:
    """
    Rechercher tous les livres recommandés pour un cursus
    
    Args:
        curriculum_id: ID du cursus
    
    Returns:
        Liste des livres de la plateforme correspondant au cursus
    """
    # Récupérer le cursus
    curriculum = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    
    if not curriculum:
        return []
    
    # Récupérer les livres recommandés pour ce cursus
    recommended_books = curriculum.recommended_books
    recommended_ids = [rb.id for rb in recommended_books]
    
    # Trouver les correspondances
    matches = db.query(BookCurriculumMatch).filter(
        BookCurriculumMatch.recommended_book_id.in_(recommended_ids),
        BookCurriculumMatch.match_score >= 70
    ).all()
    
    # Récupérer les livres
    book_ids = [m.book_id for m in matches]
    books = db.query(Book).filter(Book.id.in_(book_ids)).all()
    
    return books


def get_all_curriculums(db: Session) -> List[Curriculum]:
    """Obtenir tous les cursus disponibles"""
    return db.query(Curriculum).all()


def get_curriculum_stats(db: Session) -> Dict:
    """
    Obtenir des statistiques sur les cursus
    """
    total_curriculums = db.query(Curriculum).count()
    total_recommended = db.query(RecommendedBook).count()
    total_matches = db.query(BookCurriculumMatch).filter(
        BookCurriculumMatch.match_score >= 70
    ).count()
    
    return {
        "total_curriculums": total_curriculums,
        "total_recommended_books": total_recommended,
        "total_matches": total_matches
    }
