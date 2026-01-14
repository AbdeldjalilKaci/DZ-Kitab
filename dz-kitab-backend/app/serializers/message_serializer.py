from rest_framework import serializers
from ..models import Message
from app.moderation import is_content_safe

class MessageSerializer(serializers.ModelSerializer):
    # ton code existant ...

    def validate_content(self, value):
        if not is_content_safe(value):
            raise serializers.ValidationError("Message contenant du contenu interdit.")
        return value

class MessageSerializer(serializers.ModelSerializer):

    sender_name = serializers.CharField(source='sender.username', read_only=True)
    receiver_name = serializers.CharField(source='receiver.username', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'receiver', 'sender_name', 'receiver_name',
            'announcement', 'content', 'is_read', 'created_at'
        ]
        read_only_fields = ['sender', 'is_read', 'created_at']

    def validate(self, data):
        user = self.context['request'].user
        announcement = data['announcement']

        # L'utilisateur ne peut parler qu'au propriétaire de l'annonce
        if announcement.user != data['receiver'] and announcement.user != user:
            raise serializers.ValidationError("Conversation interdite.")

        return data
