from django.core.management.base import BaseCommand
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Book, Announcement, BookConditionScore

class Command(BaseCommand):
    help = "Seed initial data for DZ-Kitab"

    def handle(self, *args, **kwargs):
        db: Session = SessionLocal()

        # USERS
        user = User(
            email="test@dzkitab.com",
            username="testuser",
            hashed_password="hashedpassword",
            first_name="Test",
            last_name="User"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # BOOK
        book = Book(
            isbn="9781234567890",
            title="Python Programming",
            authors="Guido van Rossum",
            publisher="OpenAI Press",
            published_date="2024",
            page_count=350,
            language="fr"
        )
        db.add(book)
        db.commit()
        db.refresh(book)

        # ANNOUNCEMENT
        announcement = Announcement(
            book_id=book.id,
            user_id=user.id,
            price=2500,
            condition="BON_ETAT",
            category="INFORMATIQUE"
        )
        db.add(announcement)
        db.commit()
        db.refresh(announcement)

        # CONDITION SCORE
        score = BookConditionScore(
            announcement_id=announcement.id,
            page_no_missing=True,
            page_no_torn=True,
            page_clean=True,
            binding_no_loose=True,
            binding_no_falling=True,
            binding_stable=True,
            cover_no_detachment=True,
            cover_clean=True,
            cover_no_scratches=True,
            damage_no_burns=True,
            damage_no_smell=True,
            damage_no_insects=True,
            accessories_complete=True,
            accessories_content=True,
            accessories_extras=True
        )

        score.calculate_scores()
        score.suggest_price(base_price=3000)

        db.add(score)
        db.commit()

        self.stdout.write(self.style.SUCCESS("Seed data inserted successfully."))

