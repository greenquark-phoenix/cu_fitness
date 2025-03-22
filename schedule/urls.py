from django.urls import path
from . import views

app_name = "schedule"

urlpatterns = [
    path('generate/', views.generate_meal_schedule, name='generate_meal_schedule'),
    path('view/', views.view_meal_schedule, name='view_meal_schedule'),
]
