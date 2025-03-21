from django.shortcuts import render, get_object_or_404
from .models import WorkoutPlan, SubPlan, SubPlanExercise

def workout_plans(request):
    """ View to list all workout plans in the correct order """
    order = [
        "Beginner Fitness Plan",
        "Weight Loss & Fat Burn Plan",
        "Functional & Mobility Plan",
        "Strength & Muscle Growth Plan",
        "Athlete Performance Plan"
    ]

    all_workout_plans = WorkoutPlan.objects.all()

    # Sort workout plans based on the defined order
    ordered_plans = sorted(all_workout_plans,
                           key=lambda plan: order.index(plan.name) if plan.name in order else len(order))

    context = {"workout_plans": ordered_plans}
    return render(request, "workouts/workout_plans.html", context=context)


def workout_plan_detail(request, plan_id):
    plan = get_object_or_404(WorkoutPlan, id=plan_id)
    sub_plans = plan.sub_plans.all()  # Retrieve sub-plans related to this workout plan

    for subplan in sub_plans:
        subplan.calories_burned = subplan.total_calories()  # Compute calories

    context = {"plan": plan, "sub_plans": sub_plans}
    return render(request, "workouts/workout_plan_detail.html", context=context)


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
        selected_exercises = SubPlanExercise.objects.filter(id__in=selected_exercise_ids)
        total_calories = sum(exercise.calories_burned() for exercise in selected_exercises)

    return render(request, "workouts/workout_calories.html", {
        "subplans": subplans,
        "selected_exercises": selected_exercises,
        "total_calories": total_calories,
    })
