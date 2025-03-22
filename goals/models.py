import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

class FitnessGoal(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    unit = models.CharField(max_length=10, null=True)

    def __str__(self):
        return f"{self.name}: {self.description}"

class UserFitnessGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    goal = models.ForeignKey(FitnessGoal, on_delete=models.CASCADE, null=False, blank=False)
    target_value = models.FloatField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateField(null=False, blank=False)

    def clean(self):
        if self.target_value < 0:
            raise ValidationError("Target value must be greater than 0")

        if self.due_at < datetime.date.today():
            raise ValidationError("Due date must be greater than or equal to today")

    def __str__(self):
        return f"{self.user.username} - {self.goal.name} - {self.target_value}"


    @classmethod
    def add_new_goal(cls, user, goal, target_value, due_at):
        """
        Adds a new UserFitnessGoal after performing necessary validations.

        Parameters:
        - user: User instance
        - goal: FitnessGoal instance
        - target_value: Float, target value for the goal
        - due_at: Date, due date for the goal

        Returns:
        - UserFitnessGoal instance if created successfully

        Raises:
        - ValidationError: If any validation constraint fails
        """
        new_goal = cls(user=user, goal=goal, target_value=target_value, due_at=due_at)
        new_goal.clean()  # Ensures validations are checked explicitly
        new_goal.save()
        return new_goal
