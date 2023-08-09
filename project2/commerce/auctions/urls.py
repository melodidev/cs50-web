from django.urls import include, path
from django.contrib import admin
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("product/<str:product_title>", views.product, name="product"),
    path("user/<str:username>", views.user, name="user"),
    path("category/<str:category_id>", views.category, name="category")
]