from django.db import models
from django.contrib.auth.models import User

class Schedule(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='schedule'
    )
    # This JSON field will store the schedule as a dictionary.
    # For example:
    # {
    #   "2025-03-21": [
    #       {"meal_type": "breakfast", "meal_id": 5},
    #       {"meal_type": "lunch", "meal_id": 8},
    #       {"meal_type": "dinner", "meal_id": 12},
    #       {"meal_type": "snack", "meal_id": 3}
    #   ],
    #   "2025-03-22": [ ... ]
    # }
    scheduled_meals = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Schedule"
