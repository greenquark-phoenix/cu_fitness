from django.contrib.auth.decorators import login_required
from users.models import UserProfile
from django.shortcuts import render, get_object_or_404, redirect
from .models import WorkoutPlan, SubPlan, WorkoutCalendarEntry
from .models import  SubPlanExercise
from .models import UserWorkoutSelection
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import date, timedelta



def workout_plans(request):
    order = [
        "Beginner Fitness Plan",
        "Weight Loss & Fat Burn Plan",
        "Functional & Mobility Plan",
        "Strength & Muscle Growth Plan",
        "Athlete Performance Plan"
    ]

    all_workout_plans = WorkoutPlan.objects.all()
    ordered_plans = sorted(all_workout_plans, key=lambda plan: order.index(plan.name) if plan.name in order else len(order))

    selected_plans = []
    if request.user.is_authenticated:
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        selected_plans = user_profile.selected_workout_plans.all()

    context = {
        "workout_plans": ordered_plans,
        "selected_plans": selected_plans
    }
    return render(request, "workouts/workout_plans.html", context=context)


def workout_plan_detail(request, plan_id):
    plan = get_object_or_404(WorkoutPlan, id=plan_id)
    sub_plans = plan.sub_plans.all()

    for subplan in sub_plans:
        subplan.calories_burned = subplan.total_calories()

    selected_subplans = []
    selected_plans = []
    if request.user.is_authenticated:
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        selected_subplans = user_profile.selected_sub_plans.all()
        selected_plans = user_profile.selected_workout_plans.all()

    context = {
        "plan": plan,
        "sub_plans": sub_plans,
        "selected_subplans": selected_subplans,
        "selected_plans": selected_plans,
    }
    return render(request, "workouts/workout_plan_detail.html", context=context)


@login_required
def registered_workout_plans(request):
    user_profile = UserProfile.objects.get(user=request.user)
    selected_plans = user_profile.selected_workout_plans.all()
    selected_subplans = user_profile.selected_sub_plans.all()

    # Get entries for all selected subplans
    entries = WorkoutCalendarEntry.objects.filter(user=request.user, subplan__in=selected_subplans)

    simple_entries = {}
    total_burned_calories = 0
    total_progress_percent = 0

    for entry in entries:
        simple_entries[entry.subplan.id] = entry

        burned_kcal = entry.subplan.total_calories() * len(entry.completed_dates)
        total_days = (entry.end_date - entry.start_date).days + 1 if entry.start_date and entry.end_date else 0
        progress_percent = (len(entry.completed_dates) / total_days) * 100 if total_days > 0 else 0

        entry.burned_kcal = burned_kcal
        entry.progress_percent = round(progress_percent, 1)
        entry.total_days = total_days
        entry.completed_count = len(entry.completed_dates)

        total_burned_calories += burned_kcal
        total_progress_percent += entry.progress_percent

    average_progress = round(total_progress_percent / len(entries), 1) if entries else 0

    context = {
        "selected_plans": selected_plans,
        "selected_subplans": selected_subplans,
        "simple_entries": simple_entries,
        "total_burned_calories": total_burned_calories,
        "total_progress_percent": average_progress,
    }
    return render(request, "workouts/registered_workout_plans.html", context)



def workout_calories(request):
    """
    Displays a form allowing users to select workout exercises and calculates the total calories burned.
    Workouts are categorized by sub-plans.
    """
    subplans = SubPlan.objects.all()

    total_calories = 0
    selected_exercises = []

    if request.method == "POST":
        selected_exercise_ids = request.POST.getlist("workout_items")

        for ex in SubPlanExercise.objects.all():
            selection, _ = UserWorkoutSelection.objects.get_or_create(user=request.user, subplan_exercise=ex)
            selection.selected = str(ex.id) in selected_exercise_ids
            selection.save()

        return redirect("goals:net_calorie_chart")

    return render(request, "workouts/workout_calories.html", {
        "subplans": subplans,
        "selected_exercises": selected_exercises,
        "total_calories": total_calories,
    })


@require_POST
@login_required
def toggle_workout_selection(request):
    workout_id = request.POST.get("workout_id")
    workout_plan = get_object_or_404(WorkoutPlan, id=workout_id)
    user_profile = UserProfile.objects.get(user=request.user)

    if workout_plan in user_profile.selected_workout_plans.all():
        subplans_to_remove = workout_plan.sub_plans.all()
        user_profile.selected_sub_plans.remove(*subplans_to_remove)

        user_profile.selected_workout_plans.remove(workout_plan)
        selected = False
    else:
        user_profile.selected_workout_plans.add(workout_plan)
        selected = True

    return JsonResponse({"selected": selected})


@require_POST
@login_required
def toggle_subplan_selection(request):
    subplan_id = request.POST.get("subplan_id")
    subplan = get_object_or_404(SubPlan, id=subplan_id)

    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "UserProfile not found"}, status=400)

    print("Before:", user_profile.selected_sub_plans.all())

    if subplan in user_profile.selected_sub_plans.all():
        user_profile.selected_sub_plans.remove(subplan)
        selected = False
    else:
        user_profile.selected_sub_plans.add(subplan)
        selected = True

    print("After:", user_profile.selected_sub_plans.all())

    return JsonResponse({"selected": selected})

@login_required
def assign_simple(request):
    if request.method == "POST":
        subplan_id = request.POST.get("subplan_id")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        if subplan_id and start_date and end_date:
            WorkoutCalendarEntry.objects.update_or_create(
                user=request.user,
                subplan_id=subplan_id,
                defaults={
                    "start_date": start_date,
                    "end_date": end_date,
                    "completed_dates": []
                }
            )
    return redirect("registered_workouts")

@login_required
def remove_simple(request):
    if request.method == "POST":
        subplan_id = request.POST.get("subplan_id")
        WorkoutCalendarEntry.objects.filter(user=request.user, subplan_id=subplan_id).delete()
    return redirect("registered_workouts")

@login_required
def confirm_simple(request):
    if request.method == "POST":
        subplan_id = request.POST.get("subplan_id")
        start = request.POST.get("confirm_start")
        end = request.POST.get("confirm_end")

        if subplan_id and start and end:
            try:
                entry = WorkoutCalendarEntry.objects.get(user=request.user, subplan_id=subplan_id)

                start_date = date.fromisoformat(start)
                end_date = date.fromisoformat(end)

                # Generate list of confirmed days
                days = []
                current = start_date
                while current <= end_date:
                    days.append(current.isoformat())
                    current += timedelta(days=1)

                # Merge with existing dates, ensuring uniqueness
                entry.completed_dates = list(set(entry.completed_dates + days))
                entry.save()

            except WorkoutCalendarEntry.DoesNotExist:
                pass
    return redirect("registered_workouts")

@login_required
def remove_confirmed(request):
    if request.method == "POST":
        subplan_id = request.POST.get("subplan_id")
        try:
            entry = WorkoutCalendarEntry.objects.get(user=request.user, subplan_id=subplan_id)
            entry.completed_dates = []
            entry.save()
        except WorkoutCalendarEntry.DoesNotExist:
            pass
    return redirect("registered_workouts")

