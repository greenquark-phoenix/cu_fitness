import datetime
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User


class FitnessGoal(models.Model):
    """
    A general goal type in the system, such as weight loss, muscle gain, etc.
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
    A specific goal created by the user. For example:
    - Initial weight 80kg, target 70kg
    - Initial BMI 28, target 24
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    goal = models.ForeignKey(FitnessGoal, on_delete=models.CASCADE, null=False, blank=False)

    # 'initial_value' replaced 'starting_value'
    initial_value = models.FloatField(null=True, blank=True, default=0)
    target_value = models.FloatField(null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_at = models.DateField(null=False, blank=False)

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_started')

    def clean(self):
        """
        Basic validations:
        - target_value >= 0
        - due_at should not be earlier than today
        """
        if self.target_value < 0:
            raise ValidationError("Target value must be greater than 0")
        if self.due_at < datetime.date.today():
            raise ValidationError("Due date must be greater than or equal to today")

    @property
    def progress(self):
        """
        Calculate progress based on the latest UserFitnessProgress record.
        If no record exists, progress=0.
        This example assumes a transition from initial_value to target_value:
        ratio = (current_value - initial_value) / (target_value - initial_value)
        Adjust if needed for weight loss vs. muscle gain.
        """
        latest_progress = self.progress_logs.order_by('-timestamp').first()
        if not latest_progress:
            return 0  # No progress records

        current_value = latest_progress.current_value
        delta = self.target_value - self.initial_value
        if abs(delta) < 1e-9:
            return 0

        ratio = (current_value - self.initial_value) / delta
        # If you're doing weight loss (initial_value > target_value),
        # you might want a different formula or condition.

        ratio = max(0, min(ratio, 1))
        return round(ratio * 100, 2)

    @property
    def is_completed(self):
        """A goal is considered completed if progress >= 100%."""
        return self.progress >= 100


class UserFitnessProgress(models.Model):
    """
    A model for multiple check-ins (logs). Each time the user updates the current value,
    a new record is created here.
    """
    user_goal = models.ForeignKey(UserFitnessGoal, on_delete=models.CASCADE, related_name='progress_logs')
    current_value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Progress for Goal #{self.user_goal.id} at {self.timestamp}: {self.current_value}"
