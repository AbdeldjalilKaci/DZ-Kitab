from rest_framework import serializers
from app.models.annonce import Annonce
from app.moderation import is_content_safe

class AnnonceSerializer(serializers.ModelSerializer):
    # ton code existant ...

    def validate_title(self, value):
        if not is_content_safe(value):
            raise serializers.ValidationError("Titre contenant du contenu interdit.")
        return value

    def validate_author(self, value):
        if not is_content_safe(value):
            raise serializers.ValidationError("Nom de l'auteur contenant du contenu interdit.")
        return value

    def validate(self, data):
        # Exemple : vérifier le texte de description si tu en as
        description = data.get("description", "")
        if not is_content_safe(description):
            raise serializers.ValidationError("Description contenant du contenu interdit.")
        return data

class AnnonceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annonce
        fields = '__all__'
