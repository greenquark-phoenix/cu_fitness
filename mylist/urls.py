from django.urls import path
from . import views

app_name = 'mylist'

urlpatterns = [
    path('', views.view_mylist, name='view_mylist'),
    path('add/<int:meal_id>/', views.add_to_mylist, name='add_to_mylist'),
    path('remove/<int:meal_id>/', views.remove_from_mylist, name='remove_from_mylist'),
    path('toggle/', views.toggle_mylist, name='toggle_mylist'),
    path('toggle-workout/', views.toggle_mylist_workout, name='toggle_mylist_workout'),  # Existing endpoint
    path('remove-workout/<int:workout_id>/', views.remove_from_mylist_workout, name='remove_from_mylist_workout'),
]
