from django.urls import path

from users import views as users_views

urlpatterns = [
    path("signup/", users_views.signup, name="signup"),
]
