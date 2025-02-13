from django.urls import path
from workouts import views as workout_views

urlpatterns = [
    path("", workout_views.workout_plans, name="workout_plans_list"),
]
