from django.urls import path, include

from home import views as home_views

urlpatterns = [
    path("", home_views.index, name="home"),
]