from django.db import models

class WorkoutPlan(models.Model):
    name = models.CharField(max_length=255)
    target_group = models.CharField(max_length=255, default="General Fitness")  # Default added
    duration = models.CharField(max_length=50, default="4 Weeks")  # Default added
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)  # Default added
    focus = models.TextField(default="General fitness and well-being")  # Default added
    features = models.TextField(default="Standard workout plan features")  # Default added
    schedule = models.TextField(default="Monday - Friday training")  # Default added

    def __str__(self):
        return self.name
