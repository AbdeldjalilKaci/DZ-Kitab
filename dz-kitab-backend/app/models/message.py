from django.db import models
from app.models.user import User
from app.models.annonce import Annonce

class Message(models.Model):
    IdM = models.AutoField(primary_key=True)
    
    sender = models.ForeignKey(
        User,
        related_name='messages_envoyes',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User,
        related_name='messages_recus',
        on_delete=models.CASCADE
    )
    annonce = models.ForeignKey(
        Annonce,
        related_name='messages',
        on_delete=models.CASCADE
    )

    contenu = models.TextField()
    etat = models.BooleanField(default=False)  # False = non lu, True = lu

    # Relation N↔N avec lui-même pour gérer les réponses
    reponses = models.ManyToManyField(
        'self',
        symmetrical=False,  # False car la relation est dirigée (message → réponse)
        related_name='messages_parents',
        blank=True
    )

    class Meta:
        ordering = ['IdM']

    def __str__(self):
        return f"Message {self.IdM} de {self.sender.username} à {self.receiver.username}"
