from django.urls import path
from . import views

app_name = "goals"

urlpatterns = [
    path("", views.goal_list, name="user_goals"), # 更改了 user_goals
    path("create/", views.create_goal, name="create_goal"),
    path("update/<int:goal_id>/", views.update_goal, name="update_goal"),
    path("delete/<int:goal_id>/", views.delete_goal, name="delete_goal"),
    path("recommend/", views.recommend_goals, name="recommend_goals"),
    path("progress_notification/", views.goal_progress_notification, name="goal_progress_notification"),
    path("create_from_assistant/", views.create_goal_from_assistant, name="create_goal_from_assistant"),

    path('bmi_calculator/', views.bmi_calculator, name='bmi_calculator'), # BMI calculator
]
