from django.urls import path

from assistant import views as assistant_views

urlpatterns = [
    path("", assistant_views.assistant_view, name="assistant"),
    path("new_session", assistant_views.new_assistant_view, name="assistant_new_session"),
]
