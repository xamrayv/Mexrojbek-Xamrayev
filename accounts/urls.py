from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("verify/", views.verify_view, name="verify"),
    path("resend/", views.resend_view, name="resend"),
    path("register/", views.register_view, name="register"),
    path("telegram/", views.telegram_connect_view, name="telegram_connect"),
    path("profile/", views.profile_view, name="profile"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
