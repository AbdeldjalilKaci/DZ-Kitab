# app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.views.search_views import AnnouncementAdvancedSearchView, AnnouncementBasicSearchView
from app.views.message_views import (
    SendMessageView,
    ConversationListView,
    AnnouncementMessagesView,
    MessageViewSet  # CRUD complet DRF
)
from app.views.favorite_views import FavoriteView, FavoriteDeleteView
from app.views.annonce_views import AnnonceViewSet
from app.views.checkout_views import CheckoutView

# --- Routes classiques ---
urlpatterns = [
    # Checkout
    path('checkout/', CheckoutView.as_view(), name='checkout'),

    # Recherche annonces
    path('announcements/search/basic/', AnnouncementBasicSearchView.as_view(), name='announcement-basic-search'),
    path('announcements/search/', AnnouncementAdvancedSearchView.as_view(), name='announcement-advanced-search'),

    # Messages classiques
    path('messages/', SendMessageView.as_view(), name='send-message'),
    path('messages/conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('messages/<int:announcement_id>/', AnnouncementMessagesView.as_view(), name='announcement-messages'),

    # Favoris
    path('favorites/', FavoriteView.as_view(), name='favorite-list'),
    path('favorites/<int:id>/', FavoriteDeleteView.as_view(), name='favorite-delete'),
]

# --- Routes CRUD DRF ---
router = DefaultRouter()
router.register(r'annonces', AnnonceViewSet, basename='annonce')        # CRUD complet annonces
router.register(r'messages-crud', MessageViewSet, basename='message')   # CRUD complet messages

# Ajouter les routes DRF au urlpatterns existants
urlpatterns += router.urls

