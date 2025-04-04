from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('<int:event_id>/join/', views.join_event, name='join_event'),
    path('my-events/', views.my_events, name='my_events'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('calendar/data/', views.event_json, name='event_json'),
]
