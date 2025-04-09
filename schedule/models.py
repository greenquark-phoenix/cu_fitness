from django.db import models
from django.contrib.auth.models import User

from meals.models import Meal
from workouts.models import WorkoutPlan


class Schedule(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='schedule'
    )

    start_date = models.DateTimeField(null=False)
    end_date = models.DateTimeField(null=False)
    scheduled_meals = models.JSONField(default=dict, blank=True, null=True)
    scheduled_workouts = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Schedule"


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
