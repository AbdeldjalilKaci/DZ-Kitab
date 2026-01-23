from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from app.models.badge import Badge, UserBadge
from app.models.user import User
from app.serializers.badge_serializer import BadgeSerializer, UserBadgeSerializer

class BadgeViewSet(viewsets.ModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer

class UserBadgeViewSet(viewsets.ViewSet):
    """
    API pour attribuer des badges ou lister les badges d'un utilisateur
    """
    @action(detail=True, methods=['get'])
    def badges_utilisateur(self, request, pk=None):
        # pk = user_id
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "Utilisateur non trouvé"}, status=404)
        
        user_badges = UserBadge.objects.filter(utilisateur=user)
        serializer = UserBadgeSerializer(user_badges, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def attribuer_badge(self, request, pk=None):
        # pk = user_id, badge_id dans request.data
        badge_id = request.data.get('badge_id')
        try:
            user = User.objects.get(pk=pk)
            badge = Badge.objects.get(pk=badge_id)
        except (User.DoesNotExist, Badge.DoesNotExist):
            return Response({"error": "Utilisateur ou badge non trouvé"}, status=404)
        
        user_badge, created = UserBadge.objects.get_or_create(utilisateur=user, badge=badge)
        serializer = UserBadgeSerializer(user_badge)
        return Response(serializer.data)
