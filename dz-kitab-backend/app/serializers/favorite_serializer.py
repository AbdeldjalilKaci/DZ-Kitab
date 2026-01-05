from rest_framework import serializers
from app.models import Favorite

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'announcement', 'created_at']

    def validate(self, data):
        user = self.context['request'].user
        announcement = data['announcement']

        if Favorite.objects.filter(user=user, announcement=announcement).exists():
            raise serializers.ValidationError("Déjà ajouté aux favoris.")

        return data

    def create(self, validated_data):
        return Favorite.objects.create(
            user=self.context['request'].user,
            **validated_data
        )
