from django.urls import path
from . import views

urlpatterns = [
    path("", views.blog_list, name="blog_list"),
    path("<int:post_id>/", views.blog_detail, name="blog_detail"),
    path("post/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("comment/<int:comment_id>/like/", views.like_comment, name="like_comment"),
    path("comment/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    path("post/<int:post_id>/delete/", views.delete_post, name="delete_post"),
]
