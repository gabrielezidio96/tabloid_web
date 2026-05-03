from django.contrib import admin

from .models import Store, StoreAddress


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active']
    prepopulated_fields = {'slug': ['name']}
    list_display = ['name', 'slug', 'email', 'telephone_1', 'telephone_2', 'whatsapp', 'logo', 'has_delivery', 'has_pickup', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'has_delivery', 'has_pickup']
    search_fields = ['name', 'email', 'telephone_1', 'telephone_2', 'whatsapp']


@admin.register(StoreAddress)
class StoreAddressAdmin(admin.ModelAdmin):
    list_display = ['store', 'city', 'state', 'country', 'location', 'updated_at']
    search_fields = ['store__name', 'city', 'state', 'postal_code']
