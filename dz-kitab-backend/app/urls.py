from django.urls import path
from rest_framework.routers import DefaultRouter
from app.views.search_views import AnnouncementAdvancedSearchView
from app.views.message_views import SendMessageView, ConversationListView, AnnouncementMessagesView
from app.views.favorite_views import FavoriteView, FavoriteDeleteView
from app.views.annonce_views import AnnonceViewSet
from app.views.search_views import AnnouncementBasicSearchView


# Routes classiques
urlpatterns = [
    path('announcements/search/basic/', AnnouncementBasicSearchView.as_view(), name='announcement-basic-search'),

    path('announcements/search/', AnnouncementAdvancedSearchView.as_view(), name='announcement-advanced-search'),

    path('messages/', SendMessageView.as_view(), name='send-message'),
    path('messages/conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('messages/<int:announcement_id>/', AnnouncementMessagesView.as_view(), name='announcement-messages'),

    path('favorites/', FavoriteView.as_view()),
    path('favorites/<int:id>/', FavoriteDeleteView.as_view()),
]

# Routes CRUD DRF
router = DefaultRouter()
router.register(r'annonces', AnnonceViewSet, basename='annonce')

# Ajouter les routes DRF au urlpatterns existants
urlpatterns += router.urls
