# goals/utils.py
from datetime import date
from .models import DailyCalorieLog

def record_calories_intake(user, calories):
    today = date.today()
    log, _ = DailyCalorieLog.objects.get_or_create(user=user, date=today)
    log.calories_intake = calories
    log.save()

def record_calories_burned(user, calories):
    today = date.today()
    log, _ = DailyCalorieLog.objects.get_or_create(user=user, date=today)
    log.calories_burned = calories
    log.save()
