import datetime
import random
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from meals.models import Meal
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
    """
    Returns a nicely formatted date string, e.g. "March 21st, 2025".
    """
    day_str = ordinal_day(date_obj.day)
    month_str = date_obj.strftime('%B')
    year_str = str(date_obj.year)
    return f"{month_str} {day_str}, {year_str}"


@login_required
def generate_meal_schedule(request):
    """
    (Unchanged) Generates a 2-week schedule for the user...
    """
    schedule, _ = Schedule.objects.get_or_create(user=request.user)
    try:
        mylist = request.user.mylist
        all_meals = list(mylist.meals.all())
    except Exception:
        messages.error(request, "No meals found in your My List. Please add meals first.")
        return redirect('mylist:view_mylist')

    if not all_meals:
        messages.error(request, "Your My List is empty. Please add meals first.")
        return redirect('mylist:view_mylist')

    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=13)
    # (2-week schedule)
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

    new_schedule = {
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
        new_schedule['days'][day_str] = {
            'day_name': day_name,
            'entries': []
        }
        for mt_key in ['breakfast', 'lunch', 'dinner', 'snack']:
            if categorized_meals[mt_key]:
                chosen_meal = random.choice(categorized_meals[mt_key])
            else:
                chosen_meal = random.choice(all_meals)

            new_schedule['days'][day_str]['entries'].append({
                'meal_id': chosen_meal.id,
                'meal_type': chosen_meal.meal_type,
            })

        current_date += datetime.timedelta(days=1)

    schedule.scheduled_meals = new_schedule
    schedule.save()

    messages.success(request, "Meal schedule generated successfully for the next 2 weeks.")
    return redirect('schedule:view_meal_schedule')


@login_required
def view_meal_schedule(request):
    """
    Displays the user's meal schedule in two separate weeks, each with
    a heading like "Week 1 (March 21st, 2025 – March 27th, 2025)".
    Each day is shown as "Friday, 21-03-2025" with meal boxes below.
    """
    schedule_obj = getattr(request.user, 'schedule', None)
    if not schedule_obj or not schedule_obj.scheduled_meals:
        return render(request, 'schedule/schedule.html', {'weeks': None})

    data = schedule_obj.scheduled_meals
    metadata = data.get('metadata', {})
    days_data = data.get('days', {})

    # Build a sorted list of day objects
    sorted_days = sorted(days_data.items(), key=lambda x: x[0])  
    # => [(date_str, {day_name, entries}), ...]

    enhanced_schedule = []
    for date_str, day_info in sorted_days:
        day_name = day_info.get('day_name', '')
        date_obj = datetime.date.fromisoformat(date_str)
        # e.g. "Friday, 21-03-2025" => day_name plus DD-MM-YYYY
        display_date = f"{day_name}, {date_obj.strftime('%d-%m-%Y')}"

        # Convert each meal_id into a Meal object
        entries = []
        for item in day_info.get('entries', []):
            meal_id = item.get('meal_id')
            meal_type = item.get('meal_type')
            try:
                meal_obj = Meal.objects.get(pk=meal_id)
            except Meal.DoesNotExist:
                continue
            entries.append({
                'meal': meal_obj,
                'meal_type': meal_type,
            })

        enhanced_schedule.append({
            'date_obj': date_obj,         # store the date object for chunking
            'display_date': display_date, # e.g. "Friday, 21-03-2025"
            'entries': entries
        })

    # Now we chunk these 14 days into 2 weeks. Each chunk is 7 days.
    weeks = []
    CHUNK_SIZE = 7
    i = 0
    while i < len(enhanced_schedule):
        chunk = enhanced_schedule[i:i+CHUNK_SIZE]  # 7 days
        if chunk:
            # The week's start and end date
            week_start_date = chunk[0]['date_obj']
            week_end_date = chunk[-1]['date_obj']
            # e.g. "March 21st, 2025 – March 27th, 2025"
            week_range = f"{format_date(week_start_date)} – {format_date(week_end_date)}"
            weeks.append({
                'week_index': len(weeks) + 1,
                'week_range': week_range,
                'days': chunk,
            })
        i += CHUNK_SIZE

    context = {
        'weeks': weeks,
    }
    return render(request, 'schedule/schedule.html', context)
