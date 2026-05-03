from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        OFFER = "offer", "Offer"
        PROMO = "promo", "Promo"
        SYSTEM = "system", "System"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(max_length=10, choices=Type.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "read"]),
        ]

    def __str__(self):
        return f"{self.type}: {self.title}"


class SavedList(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_lists",
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class SavedListItem(models.Model):
    class PriceKey(models.TextChoices):
        REGULAR = "priceRegular", "Regular"
        DISCOUNTED = "priceDiscounted", "Discounted"
        APP = "priceApp", "App"
        CREDIT_CARD_CLUB = "priceCreditCardClub", "Credit Card Club"

    saved_list = models.ForeignKey(
        SavedList,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="saved_list_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    selected_price_key = models.CharField(
        max_length=30,
        choices=PriceKey.choices,
        default=PriceKey.REGULAR,
    )

    class Meta:
        unique_together = [["saved_list", "product"]]

    def __str__(self):
        return f"{self.product} x{self.quantity}"
