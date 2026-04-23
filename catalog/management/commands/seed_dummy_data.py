from datetime import date, timedelta

from django.utils.text import slugify
from django.core.management.base import BaseCommand

from stores.models import Store, StoreAddress

from catalog.models import Brand, Category, DailyFeatured, PriceSnapshot, Product


STORES = [
    {"name": "SuperMart", "slug": "supermart", "base_url": "https://supermart.example.com"},
    {"name": "FreshGrocer", "slug": "freshgrocer", "base_url": "https://freshgrocer.example.com"},
]

STORE_ADDRESSES = {
    "supermart": {
        "line_1": "Av. Paulista, 1000",
        "line_2": "Loja 1",
        "city": "Sao Paulo",
        "state": "SP",
        "postal_code": "01310-100",
        "country": "Brazil",
        "location": None,
    },
    "freshgrocer": {
        "line_1": "Rua das Laranjeiras, 250",
        "line_2": "",
        "city": "Rio de Janeiro",
        "state": "RJ",
        "postal_code": "22240-003",
        "country": "Brazil",
        "location": None,
    },
}

CATEGORIES = [
    {"name": "Dairy", "slug": "dairy"},
    {"name": "Bakery", "slug": "bakery"},
    {"name": "Beverages", "slug": "beverages"},
    {"name": "Snacks", "slug": "snacks"},
]

PRODUCTS = [
    {
        "store_slug": "supermart",
        "category_slug": "dairy",
        "name": "Whole Milk 1L",
        "brand": "FarmFresh",
        "ean": "1234567890123",
        "store_product_id": "SM-001",
        "unit": "1L",
        "regular_price": 149,
        "sale_price": 119,
        "discount_pct": "20.13",
        "is_on_sale": True,
        "is_featured": True,
    },
    {
        "store_slug": "supermart",
        "category_slug": "bakery",
        "name": "Sourdough Loaf",
        "brand": "Artisan Bakes",
        "ean": "2345678901234",
        "store_product_id": "SM-002",
        "unit": "800g",
        "regular_price": 399,
        "sale_price": None,
        "discount_pct": None,
        "is_on_sale": False,
        "is_featured": False,
    },
    {
        "store_slug": "supermart",
        "category_slug": "beverages",
        "name": "Orange Juice 2L",
        "brand": "SunPress",
        "ean": "3456789012345",
        "store_product_id": "SM-003",
        "unit": "2L",
        "regular_price": 299,
        "sale_price": 229,
        "discount_pct": "23.41",
        "is_on_sale": True,
        "is_featured": True,
    },
    {
        "store_slug": "freshgrocer",
        "category_slug": "snacks",
        "name": "Potato Chips 200g",
        "brand": "CrunchCo",
        "ean": "4567890123456",
        "store_product_id": "FG-001",
        "unit": "200g",
        "regular_price": 249,
        "sale_price": 199,
        "discount_pct": "20.08",
        "is_on_sale": True,
        "is_featured": False,
    },
    {
        "store_slug": "freshgrocer",
        "category_slug": "dairy",
        "name": "Greek Yogurt 500g",
        "brand": "Olympos",
        "ean": "5678901234567",
        "store_product_id": "FG-002",
        "unit": "500g",
        "regular_price": 349,
        "sale_price": None,
        "discount_pct": None,
        "is_on_sale": False,
        "is_featured": True,
    },
    {
        "store_slug": "freshgrocer",
        "category_slug": "beverages",
        "name": "Sparkling Water 6-pack",
        "brand": "BubblePure",
        "ean": "6789012345678",
        "store_product_id": "FG-003",
        "unit": "6x500ml",
        "regular_price": 389,
        "sale_price": 299,
        "discount_pct": "23.14",
        "is_on_sale": True,
        "is_featured": True,
    },
]


class Command(BaseCommand):
    help = "Seed the database with dummy products, prices, and featured entries"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing seed data before inserting",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            Store.objects.filter(slug__in=[s["slug"] for s in STORES]).delete()
            self.stdout.write("Cleared existing seed data.")

        today = date.today()

        stores = {}
        for s in STORES:
            store, created = Store.objects.update_or_create(
                slug=s["slug"],
                defaults={
                    "name": s["name"],
                    "base_url": s["base_url"],
                },
            )
            stores[s["slug"]] = store
            self.stdout.write(f"  {'Created' if created else 'Updated'} store: {store}")

            address_defaults = STORE_ADDRESSES.get(s["slug"])
            if address_defaults:
                _, address_created = StoreAddress.objects.update_or_create(
                    store=store,
                    defaults=address_defaults,
                )
                self.stdout.write(
                    f"    {'Created' if address_created else 'Updated'} address for: {store}"
                )

        categories = {}
        for c in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=c["slug"],
                defaults={"name": c["name"]},
            )
            categories[c["slug"]] = cat
            self.stdout.write(f"  {'Created' if created else 'Found'} category: {cat}")

        rank_by_store: dict[str, int] = {}

        for p in PRODUCTS:
            store = stores[p["store_slug"]]
            category = categories[p["category_slug"]]

            brand = None
            if p.get("brand"):
                brand, _ = Brand.objects.get_or_create(
                    slug=slugify(p["brand"]),
                    defaults={"name": p["brand"]}
                )

            product, created = Product.objects.get_or_create(
                store=store,
                store_product_id=p["store_product_id"],
                defaults={
                    "category": category,
                    "name": p["name"],
                    "brand": brand,
                    "ean": p["ean"],
                    "unit": p["unit"],
                },
            )
            self.stdout.write(f"  {'Created' if created else 'Found'} product: {product}")

            # Create price snapshots for the past 7 days
            for days_ago in range(6, -1, -1):
                snapshot_date = today - timedelta(days=days_ago)
                snapshot, _ = PriceSnapshot.objects.get_or_create(
                    product=product,
                    date=snapshot_date,
                    defaults={
                        "regular_price": p["regular_price"],
                        "sale_price": p["sale_price"],
                        "discount_pct": p["discount_pct"],
                        "is_on_sale": p["is_on_sale"],
                        "is_featured": p["is_featured"],
                    },
                )

            # Create DailyFeatured entry for today's featured products
            if p["is_featured"]:
                slug = p["store_slug"]
                rank_by_store[slug] = rank_by_store.get(slug, 0) + 1
                DailyFeatured.objects.get_or_create(
                    date=today,
                    snapshot=snapshot,
                    defaults={"store": store, "rank": rank_by_store[slug]},
                )

        self.stdout.write(self.style.SUCCESS("Done. Dummy data seeded successfully."))
