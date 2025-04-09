# File: goals/signals.py

from datetime import date

from django.db.models.signals import post_save
from django.dispatch import receiver

from goals.models import DailyCalorieLog
from meals.models import UserMealSelection
from workouts.models import UserWorkoutSelection
from goals.models import DailyCalorieLog, UserFitnessGoal
from datetime import date

# ✅ Calculate total meal calories
def calculate_total_meal_calories(user):
    selected_meals = UserMealSelection.objects.filter(user=user, selected=True)
    return sum(sel.meal.dv_calories for sel in selected_meals)

# ✅ Trigger after meal selection saved
@receiver(post_save, sender=UserMealSelection)
def update_calorie_log_on_meal_selection(sender, instance, **kwargs):
    user = instance.user
    intake = calculate_total_meal_calories(user)

    log, _ = DailyCalorieLog.objects.get_or_create(user=user, date=date.today())
    log.calories_intake = intake
    log.save()

    print("✅ Meal signal triggered for:", user.username)

# ✅ Calculate total workout calories
def calculate_total_workout_calories(user):
    selected_workouts = UserWorkoutSelection.objects.filter(user=user, selected=True)
    return sum(sel.subplan_exercise.calories_burned() for sel in selected_workouts)

# ✅ Trigger after workout selection saved
@receiver(post_save, sender=UserWorkoutSelection)
def update_calorie_log_on_workout_selection(sender, instance, **kwargs):
    user = instance.user
    burned = calculate_total_workout_calories(user)

    log, _ = DailyCalorieLog.objects.get_or_create(user=user, date=date.today())
    log.calories_burned = burned
    log.save()

    print("✅ Workout signal triggered for:", user.username)

# ✅ Automatically update weight based on net calories
def update_weight_goal_from_calories(user):
    try:
        goal = UserFitnessGoal.objects.filter(user=user, goal__name__iexact="weight").latest('created_at')
    except UserFitnessGoal.DoesNotExist:
        return

    logs = DailyCalorieLog.objects.filter(user=user).order_by('date')
    total_net_kcal = sum(log.net_calories for log in logs)
    weight_change_kg = round(total_net_kcal / 500.0, 2)  # 500 kcal → 1 kg

    goal.current_value = round(goal.starting_value + weight_change_kg, 2)
    goal.save()

    print("✅ Weight auto-updated for:", user.username, "→", goal.current_value, "kg")

# ✅ Trigger after any calorie log is saved
@receiver(post_save, sender=DailyCalorieLog)
def update_goal_after_log(sender, instance, **kwargs):
    update_weight_goal_from_calories(instance.user)
