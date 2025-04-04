from django.db import models
from django.contrib.auth.models import User
from meals.models import Meal
from workouts.models import WorkoutPlan

class MyList(models.Model):
    """One 'mylist' record per user, storing multiple meals and workout plans."""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='mylist'
    )
    meals = models.ManyToManyField(Meal, blank=True)
    workout_plans = models.ManyToManyField(WorkoutPlan, blank=True) 

    def __str__(self):
        return f"{self.user.username}'s MyList"
