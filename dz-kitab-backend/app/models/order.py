from django.db import models

class Order(models.Model):
    user_id = models.IntegerField()
    total_price = models.FloatField()
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'orders'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    announcement_id = models.IntegerField()
    quantity = models.IntegerField(default=1)
    price = models.FloatField()

    class Meta:
        managed = False
        db_table = 'order_items'
