from django.conf import settings
from django.db import models


class PostQuerySet(models.QuerySet):
    def in_vertical(self, vertical):
        return self.filter(store__vertical=vertical) if vertical else self


class PostManager(models.Manager.from_queryset(PostQuerySet)):
    pass


class Post(models.Model):
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="posts",
    )
    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.CASCADE,
        related_name="posts",
    )
    temperature = models.IntegerField(default=0)
    posted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateField(null=True, blank=True)
    limited_unit = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    objects = PostManager()

    class Meta:
        ordering = ["-posted_at"]
        indexes = [
            models.Index(fields=["is_active", "-posted_at"]),
            models.Index(fields=["is_active", "-temperature"]),
        ]

    def __str__(self):
        return f"Post: {self.product} @ {self.store}"


class PostPrice(models.Model):
    class DiscountType(models.TextChoices):
        REGULAR = "regular", "Regular"
        DISCOUNTED = "discounted", "Discounted"
        APP = "app", "App"
        CREDIT_CARD = "creditCard", "Credit Card"

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="prices")
    currency = models.CharField(max_length=3, default="BRL")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)

    class Meta:
        unique_together = [["post", "discount_type"]]

    def __str__(self):
        return f"{self.discount_type}: {self.amount}"


class PostVote(models.Model):
    class Direction(models.TextChoices):
        UP = "up", "Up"
        DOWN = "down", "Down"

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_votes",
    )
    direction = models.CharField(max_length=4, choices=Direction.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["post", "user"]]

    def __str__(self):
        return f"{self.user} {self.direction} {self.post_id}"


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
