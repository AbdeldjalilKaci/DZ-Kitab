from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from app.models import Favorite
from app.serializers.favorite_serializer import FavoriteSerializer

class FavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FavoriteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class FavoriteDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        favorite = Favorite.objects.filter(id=id, user=request.user).first()

        if not favorite:
            return Response({"detail": "Favori introuvable."}, status=404)

        favorite.delete()
        return Response(status=204)
