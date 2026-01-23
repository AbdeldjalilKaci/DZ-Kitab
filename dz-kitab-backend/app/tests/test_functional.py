from rest_framework.test import APITestCase
from rest_framework import status
from app.models.annonce import Annonce
from app.models.user import User
from app.models.order import Order
from app.models.message import Message

class FunctionalTests(APITestCase):

    def setUp(self):
        # Créer un utilisateur test
        self.user = User.objects.create(id=1, username="testuser")

        # Créer une annonce test
        self.annonce = Annonce.objects.create(
            id=1,
            title="Livre Test",
            author="Auteur Test",
            price=50.0
        )

    # --- TEST CRUD ANNONCES ---
    def test_get_annonces(self):
        response = self.client.get('/annonces/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_annonce(self):
        data = {
            "title": "Livre Nouveau",
            "author": "Auteur Nouveau",
            "price": 60.0
        }
        response = self.client.post('/annonces/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # --- TEST FAVORIS ---
    def test_add_favorite(self):
        data = {"user_id": self.user.id, "announcement_id": self.annonce.id}
        response = self.client.post('/favorites/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # --- TEST CHECKOUT ---
    def test_checkout(self):
        data = {
            "user_id": self.user.id,
            "items": [{"announcement_id": self.annonce.id, "quantity": 1}]
        }
        response = self.client.post('/checkout/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # --- TEST MODÉRATION ---
    def test_moderation_annonce(self):
        data = {"title": "Livre spam", "author": "Auteur"}
        response = self.client.post('/annonces/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
