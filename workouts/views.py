from django.shortcuts import render
from .models import WorkoutPlan

def workout_plans(request):
    all_workout_plans = WorkoutPlan.objects.all()
    context = {"workout_plans": all_workout_plans}
    return render(request, "workouts/workout_plans.html", context=context)
