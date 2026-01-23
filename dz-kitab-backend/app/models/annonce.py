from django.db import models

class Annonce(models.Model):
    isbn = models.CharField(max_length=13, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField()
    image = models.CharField(max_length=255, null=True)

    category = models.CharField(max_length=50)
    market_price = models.FloatField(null=True)
    final_calculated_price = models.FloatField(null=True)
    page_count = models.IntegerField(null=True)
    publication_date = models.CharField(max_length=50, null=True)

    class Meta:
        managed = False   # ⚠️ CRUCIAL : on ne laisse pas Django toucher la DB
        db_table = 'announcements'  # on lie au vrai nom SQL
