from django.urls import path
from .views import workout_plans, workout_plan_detail

urlpatterns = [
    path('workouts/', workout_plans, name='workouts'),  # List of all workout plans
    path('workout/<int:plan_id>/', workout_plan_detail, name='workout_plan_detail'),  # Detail page for each plan
]
