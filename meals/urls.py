from django.urls import path
from . import views

app_name = "meals"  # 这一行很重要！

urlpatterns = [
    path('', views.meal_list, name='meals_list'),  # 这个 name 必须匹配模板里的 `meals_list`
    path('intake_calories/', views.intake_calories, name='intake_calories'),
]
