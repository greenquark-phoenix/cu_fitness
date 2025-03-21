import datetime
import random
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from meals.models import Meal
from .models import Schedule

@login_required
def generate_meal_schedule(request):
    """
    Generates a meal schedule for the next 2 weeks based on the meals 
    in the user's My List. All scheduled meals are stored in a single 
    Schedule record in a JSONField.
    """
    schedule, created = Schedule.objects.get_or_create(user=request.user)
    # Retrieve meals from the user's My List
    try:
        mylist = request.user.mylist
        meals = list(mylist.meals.all())
    except Exception:
        messages.error(request, "No meals found in your My List. Please add meals first.")
        return redirect('mylist:view_mylist')
    
    if not meals:
        messages.error(request, "Your My List is empty. Please add meals first.")
        return redirect('mylist:view_mylist')
    
    # Define schedule duration: next 2 weeks (14 days)
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=13)  # 14 days total
    meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
    
    new_schedule = {}
    current_date = start_date
    while current_date <= end_date:
        day_str = current_date.isoformat()  # convert date to string
        new_schedule[day_str] = []
        for mt in meal_types:
            chosen_meal = random.choice(meals)
            new_schedule[day_str].append({
                'meal_type': mt,
                'meal_id': chosen_meal.id
            })
        current_date += datetime.timedelta(days=1)
    
    schedule.scheduled_meals = new_schedule
    schedule.save()
    
    messages.success(request, "Meal schedule generated successfully for the next 2 weeks.")
    return redirect('schedule:view_meal_schedule')

@login_required
def view_meal_schedule(request):
    """
    Displays the user's meal schedule by reading the JSONField.
    """
    schedule = getattr(request.user, 'schedule', None)
    schedule_data = schedule.scheduled_meals if schedule else {}
    return render(request, 'schedule/schedule.html', {'schedule': schedule_data})
