# schedule/views.py
import datetime
import random
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import MealSchedule
from meals.models import Meal, UserMealSelection

@login_required
def generate_meal_schedule(request):
    selected_meals = UserMealSelection.objects.filter(user=request.user, selected=True)
    if not selected_meals:
        return redirect('meals_list')

    all_meals = [s.meal for s in selected_meals]
    MealSchedule.objects.filter(user=request.user).delete()

    today = datetime.date.today()
    three_months_later = today + datetime.timedelta(days=90)
    meal_types = ["breakfast", "lunch", "dinner", "snack"]

    current_day = today
    while current_day <= three_months_later:
        for mt in meal_types:
            random_meal = random.choice(all_meals)
            MealSchedule.objects.create(
                user=request.user,
                date=current_day,
                meal_type=mt,
                meal=random_meal
            )
        current_day += datetime.timedelta(days=1)

    return redirect('schedule:view_meal_schedule')

@login_required
def view_meal_schedule(request):
    plans = MealSchedule.objects.filter(user=request.user).order_by('date', 'meal_type')
    schedule_by_date = {}
    for plan in plans:
        schedule_by_date.setdefault(plan.date, []).append(plan)

    return render(request, 'schedule.html', {
        'schedule_by_date': schedule_by_date
    })
