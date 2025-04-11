import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from meals.models import Meal
from schedule.models import MyList
from service.service import ScheduleService
from workouts.models import WorkoutPlan
# For PDF generation
from datetime import date
from django.template.loader import render_to_string
from weasyprint import HTML

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
    start_date_str = request.GET.get('start_date')
    weeks_str = request.GET.get('weeks')
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else datetime.date.today()
    except ValueError:
        start_date = datetime.date.today()

    try:
        weeks = int(weeks_str) if weeks_str else 2
        if weeks < 1:
            weeks = 1
        elif weeks > 6:
            weeks = 6
    except ValueError:
        weeks = 2

    workout_sub_plans = []
    workout_days = ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    try:
        mylist = request.user.mylist
        meals = [m.meal_name for m in mylist.meals.all()]
        if mylist.workout_plans.exists():
            workout_plan = mylist.workout_plans.first()
            sub_plans = list(workout_plan.sub_plans.all())
            index = 0
            for w in range(weeks):
                for day in workout_days:
                    sub_plan = sub_plans[index]
                    workout_sub_plans.append({
                        'day': day,
                        'name': sub_plan.name
                    })
                    index = (index + 1) % len(sub_plans)
    except Exception:
        messages.error(request, "No workouts found in your MyList. Please add meals first.")
        return redirect('schedule:view_mylist')

    username = request.user.username
    ScheduleService.create_schedule(username, start_date, weeks, meals, workout_sub_plans)
    messages.success(request, f"Meal and workout schedule generated successfully for {weeks} week(s).")
    return redirect('schedule:view_schedule')

@login_required
def view_schedule(request):
    schedule = getattr(request.user, 'schedule', None)
    if not schedule:
        return render(request, 'schedule/schedule.html', {'page_obj': None})
    schedule_days = _get_selected_days(schedule)
    meal_data = schedule.scheduled_meals or {}
    workout_data = schedule.scheduled_workouts or {}
    meal_days = {day_iso: info for day_iso, info in meal_data.items()}
    workout_days = {day_iso: info for day_iso, info in workout_data.items()}
    display_schedule = []
    for day in schedule_days:
        entry = {}
        key = day['day_str']
        date_obj = day['date_obj']
        display_date = f"{day['day_name']}, {key}"
        entry['date_obj'] = date_obj
        entry['display_date'] = display_date
        if key in workout_days:
            entry['workout'] = workout_days[key].get('workout')
            entry['workout_description'] = workout_days[key].get('workout_description')
            entry['workout_focus'] = workout_days[key].get('workout_focus')
        if key in meal_days:
            meals_by_category = {'breakfast': None, 'lunch': None, 'dinner': None, 'snack': None}
            for item in meal_days[key].get('entries', []):
                cat = item.get('meal_category')
                try:
                    meal_obj = Meal.objects.get(pk=item.get('meal_id'))
                except Meal.DoesNotExist:
                    meal_obj = None
                meals_by_category[cat] = meal_obj
            entry['meals'] = meals_by_category
        display_schedule.append(entry)
    workout_weeks = []
    CHUNK_SIZE = 7
    i = 0
    while i < len(display_schedule):
        chunk = display_schedule[i:i + CHUNK_SIZE]
        if chunk:
            week_start_date = chunk[0]['date_obj']
            week_end_date = chunk[-1]['date_obj']
            week_range = f"{format_date(week_start_date)} – {format_date(week_end_date)}"
            workout_weeks.append({
                'week_index': len(workout_weeks) + 1,
                'week_range': week_range,
                'days': chunk,
            })
        i += CHUNK_SIZE
    paginator = Paginator(workout_weeks, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'schedule/schedule.html', context)

def _get_selected_days(schedule):
    result = []
    start_date = schedule.start_date
    end_date = schedule.end_date
    current_day = start_date
    while current_day <= end_date:
        day_str = current_day.strftime('%Y-%m-%d')
        day_name = current_day.strftime('%A')
        result.append({
            'day_str': day_str,
            'day_name': day_name,
            'date_obj': current_day,
        })
        current_day += datetime.timedelta(days=1)
    return result

@login_required
def add_to_mylist(request, meal_id):
    if request.method == "POST":
        meal = get_object_or_404(Meal, pk=meal_id)
        mylist, _ = MyList.objects.get_or_create(user=request.user)
        mylist.meals.add(meal)
    return redirect('schedule:view_mylist')

@login_required
def remove_from_mylist(request, meal_id):
    if request.method == "POST":
        meal = get_object_or_404(Meal, pk=meal_id)
        mylist, _ = MyList.objects.get_or_create(user=request.user)
        mylist.meals.remove(meal)
    return redirect('schedule:view_mylist')

@login_required
def toggle_mylist(request):
    if request.method == "POST":
        meal_id = request.POST.get('meal_id')
        meal = get_object_or_404(Meal, pk=meal_id)
        mylist, _ = MyList.objects.get_or_create(user=request.user)
        if meal in mylist.meals.all():
            mylist.meals.remove(meal)
            return JsonResponse({"selected": False})
        else:
            mylist.meals.add(meal)
            return JsonResponse({"selected": True})
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def view_mylist(request):
    mylist, _ = MyList.objects.get_or_create(user=request.user)
    return render(request, 'mylist/view_mylist.html', {
        'selected_meals': mylist.meals.all(),
        'selected_workouts': mylist.workout_plans.all(),
    })

@login_required
def toggle_mylist_workout(request):
    if request.method == "POST":
        workout_id = request.POST.get("workout_id")
        plan = get_object_or_404(WorkoutPlan, pk=workout_id)
        mylist, _ = MyList.objects.get_or_create(user=request.user)
        if plan in mylist.workout_plans.all():
            mylist.workout_plans.remove(plan)
            return JsonResponse({"selected": False})
        else:
            mylist.workout_plans.add(plan)
            return JsonResponse({"selected": True})
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def remove_from_mylist_workout(request, workout_id):
    if request.method == "POST":
        plan = get_object_or_404(WorkoutPlan, pk=workout_id)
        mylist, _ = MyList.objects.get_or_create(user=request.user)
        mylist.workout_plans.remove(plan)
    return redirect('schedule:view_mylist')


# --- New: Download Report View --- #
@login_required
def download_report(request):
    # Retrieve the current user's schedule data; adjust if you need to include more data
    user_schedule = getattr(request.user, 'schedule', None)
    
    context = {
        'user': request.user,
        'report_date': date.today(),
        'schedule': user_schedule,
    }
    
    # Render the HTML template for the PDF report
    html_string = render_to_string('schedule/pdf_report.html', context)
    
    # Generate PDF using WeasyPrint
    pdf_file = HTML(string=html_string).write_pdf()
    
    # Prepare response headers with correct file naming format
    filename = f"fitness_report_{request.user.username}_{date.today()}.pdf"
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
