from django.urls import path
from .views import workout_plans, workout_plan_detail, workout_calories

app_name = "workouts"

urlpatterns = [
    path('workouts/', workout_plans, name='workouts'),
    path('workout/<int:plan_id>/', workout_plan_detail, name='workout_plan_detail'),
    path('calories/', workout_calories, name='workout_calories'),

]
