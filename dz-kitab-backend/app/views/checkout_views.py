from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.serializers.order_serializer import OrderSerializer

class CheckoutView(APIView):
    """
    Endpoint pour créer une commande sécurisée
    """
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
