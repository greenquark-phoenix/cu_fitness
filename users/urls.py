from django.urls import path

from users import views as users_views

urlpatterns = [
    path("signup/", users_views.signup_view, name="signup"),
    path('login/', users_views.login_view, name='login'),
    path('logout/', users_views.logout_view, name='logout'),
    path('profile/', users_views.profile_view, name='profile'),
]
