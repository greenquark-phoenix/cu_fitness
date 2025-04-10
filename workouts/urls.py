from django.urls import path
from . import views
from .views import (
    workout_plans,
    workout_plan_detail,
    registered_workout_plans,
    workout_calories,
    assign_simple,
    confirm_simple,
    remove_simple,
    remove_confirmed,
    toggle_workout_selection,
    toggle_subplan_selection,
)

urlpatterns = [
    # Workout plan pages
    path('workouts/', workout_plans, name='workouts'),
    path('workout/<int:plan_id>/', workout_plan_detail, name='workout_plan_detail'),

    # Log and calorie tracking
    path('registered-workouts/', registered_workout_plans, name='registered_workouts'),
    path('calories/', workout_calories, name='workout_calories'),

    # Plan/Subplan toggle selections
    path("toggle-workout/", toggle_workout_selection, name="toggle_workout_selection"),
    path("toggle-subplan/", toggle_subplan_selection, name="toggle_subplan_selection"),

    # Simple assignment and confirmation system
    path("assign-simple/", assign_simple, name="assign_simple"),
    path("remove-simple/", remove_simple, name="remove_simple"),
    path("confirm-simple/", confirm_simple, name="confirm_simple"),
    path("remove-confirmed/", remove_confirmed, name="remove_confirmed"),
]
