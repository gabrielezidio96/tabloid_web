from django.urls import path

from . import views

app_name = "deals"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("products/filter/", views.ProductGridView.as_view(), name="product-grid"),
    path("products/<int:pk>/", views.ProductDetailView.as_view(), name="product-detail"),

    path("cart/", views.CartView.as_view(), name="cart"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart-add"),
    path("cart/update/<int:pk>/", views.cart_update, name="cart-update"),
    path("cart/remove/<int:pk>/", views.cart_remove, name="cart-remove"),
    path("cart/clear/", views.cart_clear, name="cart-clear"),
    path("cart/price/<int:pk>/", views.cart_set_price, name="cart-set-price"),
    path("cart/save/", views.cart_save, name="cart-save"),

    path("notifications/", views.NotificationListView.as_view(), name="notification-list"),
    path("notifications/<int:pk>/mark/", views.notification_mark, name="notification-mark"),
    path("notifications/mark-all/", views.notification_mark_all, name="notification-mark-all"),

    path("lists/", views.SavedListListView.as_view(), name="saved-list-list"),
    path("lists/<int:pk>/", views.SavedListDetailView.as_view(), name="saved-list-detail"),
    path("lists/<int:pk>/delete/", views.saved_list_delete, name="saved-list-delete"),
    path("lists/<int:pk>/load/", views.saved_list_load, name="saved-list-load"),

    path("stores/", views.StoreListView.as_view(), name="store-list"),
    path("stores/<slug:slug>/", views.StoreDetailView.as_view(), name="store-detail"),
]
