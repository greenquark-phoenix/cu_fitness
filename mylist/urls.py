from django.urls import path
from . import views

app_name = 'mylist'

urlpatterns = [
    path('', views.view_mylist, name='view_mylist'),
    path('add/<int:meal_id>/', views.add_to_mylist, name='add_to_mylist'),
    path('remove/<int:meal_id>/', views.remove_from_mylist, name='remove_from_mylist'),
    path('toggle/', views.toggle_mylist, name='toggle_mylist'),
]
