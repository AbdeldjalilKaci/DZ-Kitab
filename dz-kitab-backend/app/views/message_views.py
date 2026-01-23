from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Max
from app.models import Message
from app.serializers.message_serializer import MessageSerializer

class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MessageSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=request.user)
        return Response(serializer.data, status=201)


class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        conversations = (
            Message.objects
            .filter(Q(sender=user) | Q(receiver=user))
            .values('announcement')
            .annotate(last_message=Max('created_at'))
            .order_by('-last_message')
        )

        return Response(conversations)


class AnnouncementMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, announcement_id):
        messages = Message.objects.filter(
            announcement_id=announcement_id
        ).filter(
            Q(sender=request.user) | Q(receiver=request.user)
        )

        return Response(MessageSerializer(messages, many=True).data)
