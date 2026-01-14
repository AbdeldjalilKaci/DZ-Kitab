
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from app.models.annonce import Annonce
from app.serializers.annonce_serializer import AnnonceSerializer
from app.pagination.announcement_pagination import AnnouncementSearchPagination

class AnnonceViewSet(ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    pagination_class = AnnouncementSearchPagination


class AnnonceViewSet(viewsets.ModelViewSet):
    """
    CRUD complet pour les annonces :
    - GET /annonces/          -> liste toutes les annonces
    - POST /annonces/         -> crée une annonce
    - GET /annonces/{id}/     -> détail d'une annonce
    - PUT /annonces/{id}/     -> mise à jour complète
    - PATCH /annonces/{id}/   -> mise à jour partielle
    - DELETE /annonces/{id}/  -> supprime une annonce
    """

    queryset = Annonce.objects.all()
    serializer_class = AnnonceSerializer
    parser_classes = [MultiPartParser, FormParser]  # pour gérer upload d'image
    permission_classes = [IsAuthenticatedOrReadOnly]  # lecture publique, écriture seulement si connecté

    # Facultatif : filtrage par titre ou author (pour recherche simple)
    def get_queryset(self):
        queryset = Annonce.objects.all()
        title = self.request.query_params.get('title')
        author = self.request.query_params.get('author')
        if title:
            queryset = queryset.filter(title__icontains=title)
        if author:
            queryset = queryset.filter(author__icontains=author)
        return queryset

