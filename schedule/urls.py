from django.urls import path
from . import views

app_name = "schedule"

urlpatterns = [
    path('generate/', views.generate_schedule, name='generate_schedule'),
    path('view/', views.view_schedule, name='view_schedule'),
    path('mylist/', views.view_mylist, name='view_mylist'),
    path('mylist/add/<int:meal_id>/', views.add_to_mylist, name='add_to_mylist'),
    path('mylist/remove/<int:meal_id>/', views.remove_from_mylist, name='remove_from_mylist'),
    path('mylist/toggle/', views.toggle_mylist, name='toggle_mylist'),
    path('mylist/toggle-workout/', views.toggle_mylist_workout, name='toggle_mylist_workout'),
    path('mylist/remove-workout/<int:workout_id>/', views.remove_from_mylist_workout, name='remove_from_mylist_workout'),
    path('download_report/', views.download_report, name='download_report'),  # New URL pattern
]
