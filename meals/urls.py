from django.urls import path
from . import views

app_name = "meals" 

urlpatterns = [
    path('', views.meal_list, name='meals_list'), 
    path('intake_calories/', views.intake_calories, name='intake_calories'),
    path('toggle_selection/', views.toggle_meal_selection, name='toggle_selection'), 
]
