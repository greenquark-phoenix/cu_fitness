from django.urls import path
from . import views

app_name = "schedule"

urlpatterns = [
    path('generate/', views.generate_schedule, name='generate_schedule'),
    path('view/', views.view_schedule, name='view_schedule'),
]
