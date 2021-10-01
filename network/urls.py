
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:profile_user>", views.profile, name="profile"),
    path("follow", views.follow, name="follow"),

    #API paths
    path("network", views.post, name="post"),
    path("update", views.update, name="update"),
    path("edit", views.edit, name="edit"),
    path("edit/<int:post_id>", views.getEditTextarea, name="getEditTextarea")
]