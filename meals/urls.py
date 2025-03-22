from django.urls import path
from . import views

urlpatterns = [
    path('', views.meal_list, name='meals_list'),
    path('toggle_selection/', views.toggle_meal_selection, name='toggle_meal_selection'),
]
