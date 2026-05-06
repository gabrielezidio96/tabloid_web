from django.contrib import admin

from .models import Brand, Category, DailyFeatured, PriceSnapshot, Product


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "parent", "verticals"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "store", "brand", "ean", "store_product_id", "created_at"]
    list_filter = ["store__vertical", "store", "category"]
    search_fields = ["name", "brand__name", "ean"]
    raw_id_fields = ["store", "category", "brand"]


@admin.register(PriceSnapshot)
class PriceSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "date",
        "regular_price",
        "sale_price",
        "discount_pct",
        "is_featured",
        "is_on_sale",
    ]
    list_filter = ["date", "is_featured", "is_on_sale", "product__store"]
    date_hierarchy = "date"
    raw_id_fields = ["product"]


@admin.register(DailyFeatured)
class DailyFeaturedAdmin(admin.ModelAdmin):
    list_display = ["date", "store", "rank", "snapshot"]
    list_filter = ["date", "store"]
    date_hierarchy = "date"
    raw_id_fields = ["snapshot", "store"]
