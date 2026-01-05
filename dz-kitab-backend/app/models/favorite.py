from django.db import models
from django.contrib.auth import get_user_model
from .announcement import Announcement

User = get_user_model()

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'announcement')

    def __str__(self):
        return f"{self.user} → {self.announcement}"
