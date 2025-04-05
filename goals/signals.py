# File: goals/signals.py

from datetime import date

from django.db.models.signals import post_save
from django.dispatch import receiver

from goals.models import DailyCalorieLog
from meals.models import UserMealSelection
from workouts.models import UserWorkoutSelection


def calculate_total_meal_calories(user):
    selected_meals = UserMealSelection.objects.filter(user=user, selected=True)
    return sum(sel.meal.dv_calories for sel in selected_meals)

@receiver(post_save, sender=UserMealSelection)
def update_calorie_log_on_meal_selection(sender, instance, **kwargs):
    user = instance.user
    intake = calculate_total_meal_calories(user)

    log, _ = DailyCalorieLog.objects.get_or_create(user=user, date=date.today())
    log.calories_intake = intake
    log.save()

def calculate_total_workout_calories(user):
    selected_workouts = UserWorkoutSelection.objects.filter(user=user, selected=True)
    return sum(sel.subplan_exercise.calories_burned() for sel in selected_workouts)

@receiver(post_save, sender=UserWorkoutSelection)
def update_calorie_log_on_workout_selection(sender, instance, **kwargs):
    user = instance.user
    burned = calculate_total_workout_calories(user)

    log, _ = DailyCalorieLog.objects.get_or_create(user=user, date=date.today())
    log.calories_burned = burned
    log.save()
