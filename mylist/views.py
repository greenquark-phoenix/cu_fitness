from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from meals.models import Meal
from workouts.models import WorkoutPlan  # Import WorkoutPlan
from .models import MyList

@login_required
def add_to_mylist(request, meal_id):
    if request.method == "POST":
        meal = get_object_or_404(Meal, pk=meal_id)
        mylist, _ = MyList.objects.get_or_create(user=request.user)
        mylist.meals.add(meal)
    return redirect('mylist:view_mylist')

@login_required
def remove_from_mylist(request, meal_id):
    if request.method == "POST":
        meal = get_object_or_404(Meal, pk=meal_id)
        mylist, _ = MyList.objects.get_or_create(user=request.user)
        mylist.meals.remove(meal)
    return redirect('mylist:view_mylist')

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
        'selected_workouts': mylist.workout_plans.all(),  # Include selected workouts
    })

# New view: Toggle Workout Plan selection via AJAX
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
