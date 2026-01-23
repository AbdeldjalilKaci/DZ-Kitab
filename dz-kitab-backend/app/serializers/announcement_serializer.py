from rest_framework import serializers
from .models import Book, Announcement

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class AnnouncementSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Announcement
        fields = '__all__'
