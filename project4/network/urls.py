
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("posts", views.posts, name="posts"),
    path("following", views.following, name="following"),
    path("like_post", views.like_post, name="like_post"),
    path("delete_like/<int:like_id>", views.delete_like, name="delete_like"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("delete_post/<int:post_id>", views.delete_post, name="delete_post"),
    path("user/<str:username>", views.user, name="user"),
    path("follow/<int:user_id>", views.follow, name="follow")
]
