from django.urls import path
from . import views

app_name = 'goals'

urlpatterns = [
    path('', views.list_user_goals, name='user_goals'),
    path('create/', views.create_goal, name='create_goal'),
    path('update/<int:pk>/', views.update_goal, name='update_goal'),
    path("net-calories/", views.net_calorie_chart, name="net_calorie_chart"),

]
