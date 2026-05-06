from django.urls import path

from . import views


app_name = "accounts"

urlpatterns = [
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("oauth/<str:provider>/", views.oauth_start, name="oauth-start"),
    path("oauth/callback/", views.oauth_callback, name="oauth-callback"),
]
