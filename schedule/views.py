# schedule/views.py

import datetime
import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import MealSchedule

@login_required
def generate_meal_schedule(request):
    """
    Temporarily disabled the old logic that used MyListItem.
    This placeholder avoids referencing removed models,
    allowing you to run makemigrations and migrate.
    """
    return redirect('mylist:view_mylist')

@login_required
def view_meal_schedule(request):
    """
    Displays the user's scheduled meals in a calendar-like format.
    """
    plans = MealSchedule.objects.filter(user=request.user).order_by('date', 'meal_type')
    schedule_by_date = {}
    for plan in plans:
        schedule_by_date.setdefault(plan.date, []).append(plan)

    return render(request, 'schedule/schedule.html', {
        'schedule_by_date': schedule_by_date
    })
