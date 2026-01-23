from rest_framework import serializers
from app.models.book import Announcement  # ou Annonce si renommé

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'  # ou liste explicite : ['id', 'book', 'user', 'price', ...]
