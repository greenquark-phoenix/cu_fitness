from django.urls import path

import schedule.views


app_name = 'mylist'

urlpatterns = [
    path('', schedule.views.view_mylist, name='view_mylist'),
    path('add/<int:meal_id>/', schedule.views.add_to_mylist, name='add_to_mylist'),
    path('remove/<int:meal_id>/', schedule.views.remove_from_mylist, name='remove_from_mylist'),
    path('toggle/', schedule.views.toggle_mylist, name='toggle_mylist'),
    path('toggle-workout/', schedule.views.toggle_mylist_workout, name='toggle_mylist_workout'),
    path('remove-workout/<int:workout_id>/', schedule.views.remove_from_mylist_workout, name='remove_from_mylist_workout'),
]
