from django.db import models
from django.contrib.auth.models import User
from meals.models import Meal

class MealSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    MEAL_TYPE_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snack"),
    ]
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPE_CHOICES)

    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.meal_type} - {self.meal.meal_name}"
    
