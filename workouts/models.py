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

class Exercise(models.Model):
    UNIT_CHOICES = [
        ("min", "Minutes"),
        ("sets", "Sets"),
        ("meters", "Meters"),
        ("rounds", "Rounds"),
    ]

    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="sets")  # New unit field
    calorie_per_unit = models.DecimalField(max_digits=5, decimal_places=2, help_text="Calories per unit (set/min/meter)")

    def __str__(self):
        return f"{self.name} ({self.unit})"

class SubPlan(models.Model):
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name="sub_plans")
    name = models.CharField(max_length=255)
    focus = models.TextField()
    schedule = models.TextField()

    def total_calories(self):
        """ Compute total calories burned across all exercises in this subplan """
        return sum(exercise.calories_burned() for exercise in self.subplanexercise_set.all())

    def __str__(self):
        return f"{self.name} ({self.workout_plan.name})"


class SubPlanExercise(models.Model):
    subplan = models.ForeignKey(SubPlan, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    duration_or_sets = models.PositiveIntegerField(help_text="Duration (minutes), sets, meters, or rounds")

    def calories_burned(self):
        """ Compute calories burned correctly and return as kcal """
        return self.exercise.calorie_per_unit * self.duration_or_sets

    def calories_display(self):
        """ Ensure kcal is correctly labeled when displayed """
        return f"{self.calories_burned()} kcal"

    def __str__(self):
        return f"{self.subplan.name} - {self.exercise.name} ({self.exercise.unit}): {self.duration_or_sets}"





from django.contrib.auth.models import User

class UserWorkoutSelection(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        subplan_exercise = models.ForeignKey(SubPlanExercise, on_delete=models.CASCADE)
        selected = models.BooleanField(default=False)

        def calories_burned(self):
            return self.subplan_exercise.calories_burned()

        def __str__(self):
            return f"{self.user.username} - {self.subplan_exercise} - selected={self.selected}"

