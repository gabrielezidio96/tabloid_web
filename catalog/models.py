from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    image_url = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    image_url = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    class UnitType(models.TextChoices):
        UNIT = "unit", "un"
        KG = "kg", "kg"
        G = "g", "g"
        L = "l", "L"
        ML = "ml", "mL"

    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.CASCADE,
        related_name="products",
    )
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
    )
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(
        Brand,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
    )
    ean = models.CharField(max_length=13, blank=True, db_index=True)
    store_product_id = models.CharField(max_length=100, blank=True)
    product_url = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    thumb_image_url = models.URLField(blank=True)
    unit = models.CharField(max_length=30, blank=True)
    unit_type = models.CharField(
        max_length=10,
        choices=UnitType.choices,
        blank=True,
    )
    limited_unit = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["store", "store_product_id"]]
        indexes = [
            models.Index(fields=["store", "ean"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.store})"


class PriceSnapshot(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="snapshots"
    )
    scraped_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField(db_index=True)

    # Prices stored as integer cents to avoid float precision bugs
    regular_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_app = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_credit_card_club = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    currency = models.CharField(max_length=3, default="BRL")

    discount_pct = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    is_featured = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["date", "is_featured"]),
            models.Index(fields=["date", "discount_pct"]),
            models.Index(fields=["product", "date"]),
        ]

    def __str__(self):
        return f"{self.product} @ {self.date}"


class DailyFeatured(models.Model):
    date = models.DateField(db_index=True)
    snapshot = models.ForeignKey(PriceSnapshot, on_delete=models.CASCADE)
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE)
    rank = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = [["date", "snapshot"]]
        ordering = ["date", "rank"]

    def __str__(self):
        return f"{self.store} #{self.rank} on {self.date}"
