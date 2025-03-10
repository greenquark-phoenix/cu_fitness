from django.db import models

class WorkoutPlan(models.Model):
    name = models.CharField(max_length=255)
    target_group = models.CharField(max_length=255)
    duration = models.CharField(max_length=50, default="4 Weeks")
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    focus = models.TextField(default="General fitness and well-being")
    features = models.TextField(default="Standard workout plan features")
    schedule = models.TextField(default="Monday - Friday training")

    def __str__(self):
        return self.name

class SubPlan(models.Model):
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name="sub_plans")
    name = models.CharField(max_length=255)
    focus = models.TextField()
    equipment = models.TextField()
    schedule = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.workout_plan.name})"
