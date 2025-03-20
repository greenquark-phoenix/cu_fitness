import datetime
import random
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import MealSchedule
from meals.models import Meal, UserMealSelection  # or wherever your "selected" logic is

@login_required
def generate_meal_schedule(request):
    # Retrieve the user’s selected meals (or however you store "selected" status)
    selected_meals = UserMealSelection.objects.filter(user=request.user, selected=True)
    if not selected_meals:
        return redirect('meals_list')  # Or show a message that no meals are selected

    # Convert selected meals to a simple list of Meal objects
    all_meals = [s.meal for s in selected_meals]

    # Clear old schedule
    MealSchedule.objects.filter(user=request.user).delete()

    #Define the 3-month range
    today = datetime.date.today()
    three_months_later = today + datetime.timedelta(days=90)

    # Define meal types
    meal_types = ["breakfast", "lunch", "dinner", "snack"]

    # Loop over each day in that 3-month window
    current_day = today
    while current_day <= three_months_later:
        for mt in meal_types:
            # Pick a random meal from the user’s selected meals
            random_meal = random.choice(all_meals)
            # Save a record to MealSchedule
            MealSchedule.objects.create(
                user=request.user,
                date=current_day,
                meal_type=mt,
                meal=random_meal
            )
        current_day += datetime.timedelta(days=1)

    # Redirect to a page that displays the newly created schedule
    return redirect('schedule:view_meal_schedule')

@login_required
def view_meal_schedule(request):
    # Get all scheduled meals for this user, sorted by date then meal_type
    plans = MealSchedule.objects.filter(user=request.user).order_by('date', 'meal_type')

    # Group them by date (for easier display)
    schedule_by_date = {}
    for plan in plans:
        schedule_by_date.setdefault(plan.date, []).append(plan)

    # Render a template that shows the schedule
    return render(request, 'schedule/view_schedule.html', {
        'schedule_by_date': schedule_by_date
    })
