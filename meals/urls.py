from django.urls import path
from . import views

urlpatterns = [
    path('', views.meal_list, name='meals_list'),
    path('toggle_selection/', views.toggle_meal_selection, name='toggle_meal_selection'),
    path('intake_calories/', views.intake_calories, name='intake_calories'),
]
