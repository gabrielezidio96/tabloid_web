from django.contrib import admin

from .models import Store, StoreAddress


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active']
    prepopulated_fields = {'slug': ['name']}


@admin.register(StoreAddress)
class StoreAddressAdmin(admin.ModelAdmin):
    list_display = ['store', 'city', 'state', 'country', 'location', 'updated_at']
    search_fields = ['store__name', 'city', 'state', 'postal_code']
