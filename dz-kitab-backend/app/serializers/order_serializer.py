from rest_framework import serializers
from app.models.order import Order, OrderItem
from app.models.annonce import Annonce
from app.models.user import User  # adapte selon ton modèle user

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['announcement_id', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user_id', 'total_price', 'status', 'created_at', 'items']
        read_only_fields = ['total_price', 'status', 'created_at']

    def validate_user_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Utilisateur inexistant.")
        return value

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("La commande ne peut pas être vide.")
        for item in value:
            if not Annonce.objects.filter(id=item['announcement_id']).exists():
                raise serializers.ValidationError(f"Annonce {item['announcement_id']} inexistante.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        total_price = 0

        for item in items_data:
            annonce = Annonce.objects.get(id=item['announcement_id'])
            item['price'] = annonce.price
            total_price += annonce.price * item.get('quantity', 1)

        order = Order.objects.create(
            user_id=validated_data['user_id'],
            total_price=total_price,
            status='Pending'
        )

        for item in items_data:
            OrderItem.objects.create(
                order=order,
                announcement_id=item['announcement_id'],
                quantity=item.get('quantity', 1),
                price=item['price']
            )

        return order
