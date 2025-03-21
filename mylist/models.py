from django.db import models
from django.contrib.auth.models import User
from meals.models import Meal

class MyListItem(models.Model):
    """
    A record of a single meal that the user has added to their 'mylist'.
    In future, you could also link workouts, etc.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'meal')  # Prevent duplicates for the same user+meal

    def __str__(self):
        return f"{self.user.username} -> {self.meal.meal_name}"
