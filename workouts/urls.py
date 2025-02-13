from django.urls import path
from .views import WopListView

urlpatterns = [
    path("", WopListView.as_view(), name="wop_list"),  # The empty string matches the root of '/woplan/'
]
