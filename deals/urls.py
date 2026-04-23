from django.urls import path

from . import views

app_name = "deals"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("products/filter/", views.ProductGridView.as_view(), name="product-grid"),
]
