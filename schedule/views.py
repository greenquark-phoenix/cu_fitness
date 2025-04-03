import datetime
import random
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404

from meals.models import Meal
from workouts.models import WorkoutPlan
from .models import Schedule

def ordinal_day(day):
    if 11 <= day <= 13:
        return f"{day}th"
    elif day % 10 == 1:
        return f"{day}st"
    elif day % 10 == 2:
        return f"{day}nd"
    elif day % 10 == 3:
        return f"{day}rd"
    else:
        return f"{day}th"

def format_date(date_obj):
    day_str = ordinal_day(date_obj.day)
    month_str = date_obj.strftime('%B')
    year_str = str(date_obj.year)
    return f"{month_str} {day_str}, {year_str}"

@login_required
def generate_schedule(request):
    """
    Generates a combined schedule for meals and workouts.
    Meals: For each day, for each category (breakfast, lunch, dinner, snack),
           if the user has selected any meals in that category, one is chosen;
           otherwise, that meal slot remains empty.
    Workouts: If a workout plan is selected (only one allowed),
              assign its subplans to weekdays (Monday–Friday) and mark weekends as "Rest Day".
              Also store the subplan's schedule (description) and focus.
    """
    schedule, _ = Schedule.objects.get_or_create(user=request.user)
    
    # ----- MEALS SCHEDULE -----
    try:
        mylist = request.user.mylist
        all_meals = list(mylist.meals.all())
    except Exception:
        messages.error(request, "No meals found in your MyList. Please add meals first.")
        return redirect('mylist:view_mylist')

    if not all_meals:
        messages.error(request, "Your MyList is empty. Please add meals first.")
        return redirect('mylist:view_mylist')

    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=13)  # 2-week schedule

    # Categorize meals by type—only those selected by the user.
    categorized_meals = {
        'breakfast': [],
        'lunch': [],
        'dinner': [],
        'snack': []
    }
    for meal in all_meals:
        mt_lower = meal.meal_type.lower()
        if mt_lower in categorized_meals:
            categorized_meals[mt_lower].append(meal)

    meal_schedule = {
        'metadata': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'days': {}
    }

    current_date = start_date
    while current_date <= end_date:
        day_str = current_date.isoformat()
        day_name = current_date.strftime('%A')
        # For each day, only add a meal for a category if available.
        day_entries = []
        for mt_key in ['breakfast', 'lunch', 'dinner', 'snack']:
            if categorized_meals[mt_key]:
                chosen_meal = random.choice(categorized_meals[mt_key])
                day_entries.append({
                    'meal_id': chosen_meal.id,
                    'meal_type': chosen_meal.meal_type,
                    'meal_category': mt_key,
                })
        meal_schedule['days'][day_str] = {
            'day_name': day_name,
            'entries': day_entries
        }
        current_date += datetime.timedelta(days=1)

    # ----- WORKOUTS SCHEDULE -----
    workout_schedule = None
    if mylist.workout_plans.exists():
        workout_plan = mylist.workout_plans.first()
        # Retrieve subplans in order (assume 5 subplans exist)
        subplans = list(workout_plan.sub_plans.all().order_by('pk'))
        workout_schedule = {
            'metadata': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'weeks': []
        }
        current_week_start = start_date
        while current_week_start <= end_date:
            week_days = {}
            for i in range(7):
                day = current_week_start + datetime.timedelta(days=i)
                day_name = day.strftime('%A')
                if day.weekday() < 5:  # Monday to Friday
                    if day.weekday() < len(subplans):
                        subplan = subplans[day.weekday()]
                        assigned_workout = subplan.name
                        # Provide fallback if fields are empty
                        workout_description = subplan.schedule.strip() or "No schedule info provided"
                        workout_focus = subplan.focus.strip() or "No focus info provided"
                    else:
                        assigned_workout = "Workout"
                        workout_description = "No schedule info provided"
                        workout_focus = "No focus info provided"
                else:
                    assigned_workout = "Rest Day"
                    workout_description = ""
                    workout_focus = ""
                week_days[day.isoformat()] = {
                    'day_name': day_name,
                    'workout': assigned_workout,
                    'workout_description': workout_description,
                    'workout_focus': workout_focus,
                }
            week_range = f"{format_date(current_week_start)} – {format_date(current_week_start + datetime.timedelta(days=6))}"
            workout_schedule['weeks'].append({
                'week_range': week_range,
                'days': week_days,
            })
            current_week_start += datetime.timedelta(days=7)

    # ----- COMBINE SCHEDULES -----
    combined_schedule = {
        'meals': meal_schedule,
        'workouts': workout_schedule  # May be None if no workout plan is selected.
    }
    schedule.scheduled_meals = combined_schedule
    schedule.save()

    messages.success(request, "Meal and workout schedule generated successfully for the next 2 weeks.")
    return redirect('schedule:view_schedule')

@login_required
def view_schedule(request):
    """
    Displays the combined schedule.
    The meal schedule is grouped into days and then into weekly chunks (with pagination).
    For each day, meals are grouped by category and the workout data (including its description and focus)
    is merged from the workout schedule lookup.
    """
    schedule_obj = getattr(request.user, 'schedule', None)
    if not schedule_obj or not schedule_obj.scheduled_meals:
        return render(request, 'schedule/schedule.html', {'page_obj': None})

    data = schedule_obj.scheduled_meals
    meal_data = data.get('meals', {})
    workout_data = data.get('workouts', None)

    # Build a lookup dictionary for workouts (mapping ISO date to a dict with workout info).
    workout_lookup = {}
    if workout_data:
        for week in workout_data.get('weeks', []):
            for day_iso, info in week.get('days', {}).items():
                workout_lookup[day_iso] = {
                    'workout': info.get('workout'),
                    'workout_description': info.get('workout_description'),
                    'workout_focus': info.get('workout_focus'),
                }

    sorted_meal_days = sorted(meal_data.get('days', {}).items(), key=lambda x: x[0])
    enhanced_schedule = []
    for date_str, day_info in sorted_meal_days:
        date_obj = datetime.date.fromisoformat(date_str)
        display_date = f"{day_info.get('day_name')}, {date_obj.strftime('%d-%m-%Y')}"
        # Group meals by category. Initialize all to None.
        meals_by_category = {'breakfast': None, 'lunch': None, 'dinner': None, 'snack': None}
        for item in day_info.get('entries', []):
            cat = item.get('meal_category')
            try:
                meal_obj = Meal.objects.get(pk=item.get('meal_id'))
            except Meal.DoesNotExist:
                meal_obj = None
            meals_by_category[cat] = meal_obj
        enhanced_schedule.append({
            'date_obj': date_obj,
            'display_date': display_date,
            'meals': meals_by_category,
            'workout': workout_lookup.get(date_str, {}).get('workout'),
            'workout_description': workout_lookup.get(date_str, {}).get('workout_description'),
            'workout_focus': workout_lookup.get(date_str, {}).get('workout_focus'),
        })

    # Group days into weeks (7 days per week)
    weeks = []
    CHUNK_SIZE = 7
    i = 0
    while i < len(enhanced_schedule):
        chunk = enhanced_schedule[i:i+CHUNK_SIZE]
        if chunk:
            week_start_date = chunk[0]['date_obj']
            week_end_date = chunk[-1]['date_obj']
            week_range = f"{format_date(week_start_date)} – {format_date(week_end_date)}"
            weeks.append({
                'week_index': len(weeks) + 1,
                'week_range': week_range,
                'days': chunk,
            })
        i += CHUNK_SIZE

    paginator = Paginator(weeks, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'schedule/schedule.html', context)
