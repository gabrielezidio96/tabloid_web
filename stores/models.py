from django.contrib.gis.db import models


class StoreQuerySet(models.QuerySet):
    def in_vertical(self, vertical):
        return self.filter(vertical=vertical) if vertical else self

    def active_in_vertical(self, vertical):
        return self.filter(is_active=True).in_vertical(vertical)


class StoreManager(models.Manager.from_queryset(StoreQuerySet)):
    pass


class Store(models.Model):
    class Vertical(models.TextChoices):
        SUPERMARKET = 'supermarket', 'Mercado'
        PHARMACY = 'pharmacy', 'Farmácia'

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    vertical = models.CharField(
        max_length=20,
        choices=Vertical.choices,
        default=Vertical.SUPERMARKET,
        db_index=True,
    )
    email = models.EmailField()
    telephone_1 = models.CharField(max_length=20, blank=True, null=True)
    telephone_2 = models.CharField(max_length=20, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    logo = models.ImageField(upload_to='stores/logos/', blank=True)
    has_delivery = models.BooleanField(default=False)
    has_pickup = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = StoreManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class StoreAddress(models.Model):
    store = models.OneToOneField(
        Store,
        on_delete=models.CASCADE,
        related_name='address',
    )
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    number = models.CharField(max_length=20)
    complement = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Brazil')
    location = models.PointField(srid=4326, geography=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['store__name']

    def __str__(self):
        return f'{self.store.name} address'
