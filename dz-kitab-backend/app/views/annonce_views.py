from rest_framework import viewsets, permissions
from app.models.book import Announcement
from app.serializers.annonce_serializer import AnnouncementSerializer

class AnnonceViewSet(viewsets.ModelViewSet):
    """
    CRUD complet pour les annonces
    """
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]  # ou IsAdminUser si nécessaire

    def perform_create(self, serializer):
        # On lie automatiquement l'annonce à l'utilisateur connecté
        serializer.save(user=self.request.user)


