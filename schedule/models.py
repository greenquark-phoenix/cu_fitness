from django.db import models
from django.contrib.auth.models import User

class Schedule(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='schedule'
    )
    # All scheduled meals stored as JSON (one record per user)
    scheduled_meals = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Schedule"
