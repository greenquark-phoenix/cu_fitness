from django.contrib import admin
from goals.models import FitnessGoal, UserFitnessGoal, DailyCalorieLog  # Importing models


@admin.register(FitnessGoal)
class FitnessGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'unit')  # Display these fields in the admin list view


@admin.register(UserFitnessGoal)
class UserFitnessGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal', 'target_value', 'current_value', 'due_at')  # Show goal-related details per user


@admin.register(DailyCalorieLog)
class DailyCalorieLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'calories_intake', 'calories_burned', 'net_calories')  # Include calculated net calories
    list_filter = ('user', 'date')  # Add filters by user and date for easy navigation
