import datetime
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

class FitnessGoal(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    unit = models.CharField(max_length=10, null=True)

    CATEGORY_CHOICES = [
        ('bmi_target', 'BMI target'),
        ('weight_loss', 'Weight loss'),
        ('muscle_gain', 'Muscle gain'),
        ('endurance', 'Endurance training'),
        ('custom', 'Custom'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='custom')

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class UserFitnessGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    goal = models.ForeignKey(FitnessGoal, on_delete=models.CASCADE, null=False, blank=False)
    target_value = models.FloatField(null=False, blank=False)
    starting_value = models.FloatField(null=True, blank=True, default=0)  # Default to 0
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # For displaying the latest update time
    due_at = models.DateField(null=False, blank=False)

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_started')

    def clean(self):
        # Ensure the target value is greater than or equal to 0
        if self.target_value < 0:
            raise ValidationError("Target value must be greater than 0")
        # Ensure the due date is not earlier than today
        if self.due_at < datetime.date.today():
            raise ValidationError("Due date must be greater than or equal to today")

    @property
    def progress(self):
        """
        Calculate goal progress:
        Current formula: ((starting_value - target_value) / abs(starting_value - target_value)) * 100
        Note: If you want a more accurate linear progress, you may need to adjust the logic.
        """
        if self.starting_value is None or self.target_value is None:
            return 0
        if abs(self.starting_value - self.target_value) < 0.0001:
            return 100  # Avoid division by zero; also means goal is effectively completed
        progress = ((self.starting_value - self.target_value) / abs(self.starting_value - self.target_value)) * 100
        return max(0, min(progress, 100))  # Constrain progress to 0%-100%
