from django.db import models
from app.models.user import User

class Badge(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    icone = models.CharField(max_length=255, blank=True, null=True)  # URL ou nom d'icône

    def __str__(self):
        return self.nom

class UserBadge(models.Model):
    utilisateur = models.ForeignKey(User, related_name="badges", on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, related_name="utilisateurs", on_delete=models.CASCADE)
    date_attribue = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('utilisateur', 'badge')

    def __str__(self):
        return f"{self.utilisateur.username} - {self.badge.nom}"
