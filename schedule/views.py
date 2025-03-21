import datetime
import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from mylist.models import MyListItem
from .models import MealSchedule

@login_required
def generate_meal_schedule(request):
    mylist_items = MyListItem.objects.filter(user=request.user)
    if not mylist_items.exists():
        return redirect('mylist:view_mylist')

    all_meals = [item.meal for item in mylist_items]
    MealSchedule.objects.filter(user=request.user).delete()

    today = datetime.date.today()
    three_months_later = today + datetime.timedelta(days=90)
    meal_types = ["breakfast", "lunch", "dinner", "snack"]

    current_day = today
    while current_day <= three_months_later:
        for mt in meal_types:
            chosen_meal = random.choice(all_meals)
            MealSchedule.objects.create(
                user=request.user,
                date=current_day,
                meal_type=mt,
                meal=chosen_meal
            )
        current_day += datetime.timedelta(days=1)

    return redirect('schedule:view_meal_schedule')


@login_required
def view_meal_schedule(request):
    # This is the missing function
    plans = MealSchedule.objects.filter(user=request.user).order_by('date', 'meal_type')
    schedule_by_date = {}
    for plan in plans:
        schedule_by_date.setdefault(plan.date, []).append(plan)

    return render(request, 'schedule/schedule.html', {
        'schedule_by_date': schedule_by_date
    })
