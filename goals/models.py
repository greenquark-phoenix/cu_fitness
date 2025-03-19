import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class FitnessGoal(models.Model):
    """
    Represents a general goal type, such as weight loss or muscle gain.
    """
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    unit = models.CharField(max_length=10, null=True)

    CATEGORY_CHOICES = [
        ('bmi_target', 'BMI Target'),
        ('weight_loss', 'Weight Loss Target'),
        ('muscle_gain', 'Muscle Gain Target'),
        ('endurance', 'Endurance Training'),
        ('custom', 'Custom'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='custom')

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class UserFitnessGoal(models.Model):
    """
    A specific goal created by the user, for example:
    initial_value=80kg, target_value=70kg, due_at in 2 months, etc.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal = models.ForeignKey(FitnessGoal, on_delete=models.CASCADE)
    initial_value = models.FloatField(null=True, blank=True, default=0)
    target_value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_at = models.DateField()

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_started')

    def clean(self):
        if self.target_value < 0:
            raise ValidationError("Target value must be greater than 0.")
        if self.due_at < datetime.date.today():
            raise ValidationError("Due date must be today or later.")

    @property
    def progress(self):
        """
        Calculates progress based on the latest UserFitnessProgress record.
        If no record exists, returns 0.
        """
        latest_log = self.progress_logs.order_by('-timestamp').first()
        if not latest_log:
            return 0
        current_value = latest_log.current_value
        delta = self.target_value - self.initial_value
        if abs(delta) < 1e-9:
            return 0
        ratio = (current_value - self.initial_value) / delta
        ratio = max(0, min(ratio, 1))
        return round(ratio * 100, 2)

    @property
    def is_completed(self):
        return self.progress >= 100

    def __str__(self):
        return f"Goal #{self.id} for {self.user.username}"


class UserFitnessProgress(models.Model):
    """
    Logs multiple check-ins for each goal.
    """
    user_goal = models.ForeignKey(UserFitnessGoal, on_delete=models.CASCADE, related_name='progress_logs')
    current_value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Progress for Goal #{self.user_goal.id} at {self.timestamp}: {self.current_value}"
