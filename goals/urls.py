from django.urls import path
from goals import views as goal_views

urlpatterns = [
    path('', goal_views.list_user_goals, name='user_goals')
]
