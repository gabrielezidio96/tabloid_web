import random
from datetime import date, timedelta

from django.contrib.gis.geos import Point
from django.utils.text import slugify
from django.core.management.base import BaseCommand

from stores.models import Store, StoreAddress

from catalog.models import Brand, Category, DailyFeatured, PriceSnapshot, Product
from deals.models import Post, PostPrice


STORES = [
    {
        "name": "SuperMart",
        "slug": "supermart",
        "email": "contato@supermart.example.com",
        "telephone_1": "+55 11 3000-1000",
        "telephone_2": "+55 11 3000-1001",
        "whatsapp": "+55 11 99999-1000",
        "has_delivery": True,
        "has_pickup": True,
    },
    {
        "name": "FreshGrocer",
        "slug": "freshgrocer",
        "email": "contato@freshgrocer.example.com",
        "telephone_1": "+55 21 3000-2000",
        "telephone_2": None,
        "whatsapp": "+55 21 99999-2000",
        "has_delivery": False,
        "has_pickup": True,
    },
]

STORE_ADDRESSES = {
    "supermart": {
        "address_line_1": "Av. Paulista",
        "address_line_2": "",
        "number": "1000",
        "complement": "Loja 1",
        "district": "Bela Vista",
        "city": "Sao Paulo",
        "state": "SP",
        "zip_code": "01310-100",
        "country": "Brazil",
        "location": Point(-46.6544, -23.5644, srid=4326),
    },
    "freshgrocer": {
        "address_line_1": "Rua das Laranjeiras",
        "address_line_2": "",
        "number": "250",
        "complement": "",
        "district": "Laranjeiras",
        "city": "Rio de Janeiro",
        "state": "RJ",
        "zip_code": "22240-003",
        "country": "Brazil",
        "location": Point(-43.1822, -22.9360, srid=4326),
    },
}

CATEGORIES = [
    {"name": "Dairy", "slug": "dairy"},
    {"name": "Bakery", "slug": "bakery"},
    {"name": "Beverages", "slug": "beverages"},
    {"name": "Snacks", "slug": "snacks"},
    {"name": "Produce", "slug": "produce"},
    {"name": "Meat & Poultry", "slug": "meat-poultry"},
    {"name": "Frozen", "slug": "frozen"},
    {"name": "Pantry", "slug": "pantry"},
    {"name": "Cleaning", "slug": "cleaning"},
    {"name": "Personal Care", "slug": "personal-care"},
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
    {
        "store_slug": "supermart",
        "category_slug": "dairy",
        "name": "Salted Butter 200g",
        "brand": "FarmFresh",
        "ean": "7890123456789",
        "store_product_id": "SM-004",
        "unit": "200g",
        "regular_price": 1299,
        "sale_price": 999,
        "discount_pct": "23.10",
        "is_on_sale": True,
        "is_featured": False,
    },
    {
        "store_slug": "supermart",
        "category_slug": "dairy",
        "name": "Mozzarella Cheese 400g",
        "brand": "Tirolez",
        "ean": "7890123456790",
        "store_product_id": "SM-005",
        "unit": "400g",
        "regular_price": 2499,
        "sale_price": None,
        "discount_pct": None,
        "is_on_sale": False,
        "is_featured": False,
    },
    {
        "store_slug": "supermart",
        "category_slug": "bakery",
        "name": "Croissant 4-pack",
        "brand": "Artisan Bakes",
        "ean": "7890123456791",
        "store_product_id": "SM-006",
        "unit": "4x80g",
        "regular_price": 899,
        "sale_price": 699,
        "discount_pct": "22.25",
        "is_on_sale": True,
        "is_featured": True,
    },
    {
        "store_slug": "supermart",
        "category_slug": "produce",
        "name": "Bananas",
        "brand": None,
        "ean": "7890123456792",
        "store_product_id": "SM-007",
        "unit": "1kg",
        "regular_price": 599,
        "sale_price": 449,
        "discount_pct": "25.04",
        "is_on_sale": True,
        "is_featured": False,
    },
    {
        "store_slug": "supermart",
        "category_slug": "produce",
        "name": "Roma Tomatoes",
        "brand": None,
        "ean": "7890123456793",
        "store_product_id": "SM-008",
        "unit": "1kg",
        "regular_price": 799,
        "sale_price": None,
        "discount_pct": None,
        "is_on_sale": False,
        "is_featured": False,
    },
    {
        "store_slug": "supermart",
        "category_slug": "meat-poultry",
        "name": "Chicken Breast",
        "brand": "Sadia",
        "ean": "7890123456794",
        "store_product_id": "SM-009",
        "unit": "1kg",
        "regular_price": 2899,
        "sale_price": 1999,
        "discount_pct": "31.04",
        "is_on_sale": True,
        "is_featured": True,
    },
    {
        "store_slug": "supermart",
        "category_slug": "meat-poultry",
        "name": "Ground Beef 80/20",
        "brand": "Friboi",
        "ean": "7890123456795",
        "store_product_id": "SM-010",
        "unit": "500g",
        "regular_price": 2299,
        "sale_price": 1799,
        "discount_pct": "21.75",
        "is_on_sale": True,
        "is_featured": False,
    },
    {
        "store_slug": "supermart",
        "category_slug": "pantry",
        "name": "White Rice 5kg",
        "brand": "Tio Joao",
        "ean": "7890123456796",
        "store_product_id": "SM-011",
        "unit": "5kg",
        "regular_price": 3499,
        "sale_price": 2799,
        "discount_pct": "20.01",
        "is_on_sale": True,
        "is_featured": True,
    },
    {
        "store_slug": "supermart",
        "category_slug": "pantry",
        "name": "Black Beans 1kg",
        "brand": "Camil",
        "ean": "7890123456797",
        "store_product_id": "SM-012",
        "unit": "1kg",
        "regular_price": 999,
        "sale_price": None,
        "discount_pct": None,
        "is_on_sale": False,
        "is_featured": False,
    },
    {
        "store_slug": "supermart",
        "category_slug": "pantry",
        "name": "Extra Virgin Olive Oil 500ml",
        "brand": "Gallo",
        "ean": "7890123456798",
        "store_product_id": "SM-013",
        "unit": "500ml",
        "regular_price": 3999,
        "sale_price": 2999,
        "discount_pct": "25.01",
        "is_on_sale": True,
        "is_featured": True,
    },
    {
        "store_slug": "supermart",
        "category_slug": "snacks",
        "name": "Chocolate Cookies 150g",
        "brand": "Bauducco",
        "ean": "7890123456799",
        "store_product_id": "SM-014",
        "unit": "150g",
        "regular_price": 599,
        "sale_price": 399,
        "discount_pct": "33.39",
        "is_on_sale": True,
        "is_featured": False,
    },
    {
        "store_slug": "supermart",
        "category_slug": "frozen",
        "name": "Frozen Pizza Margherita",
        "brand": "Sadia",
        "ean": "7890123456800",
        "store_product_id": "SM-015",
        "unit": "460g",
        "regular_price": 1899,
        "sale_price": 1399,
        "discount_pct": "26.33",
        "is_on_sale": True,
        "is_featured": True,
    },
    {
        "store_slug": "supermart",
        "category_slug": "cleaning",
        "name": "Laundry Detergent 3L",
        "brand": "Omo",
        "ean": "7890123456801",
        "store_product_id": "SM-016",
        "unit": "3L",
        "regular_price": 3499,
        "sale_price": None,
        "discount_pct": None,
        "is_on_sale": False,
        "is_featured": False,
    },
    {
        "store_slug": "supermart",
        "category_slug": "personal-care",
        "name": "Toothpaste 90g",
        "brand": "Colgate",
        "ean": "7890123456802",
        "store_product_id": "SM-017",
        "unit": "90g",
        "regular_price": 799,
        "sale_price": 599,
        "discount_pct": "25.03",
        "is_on_sale": True,
        "is_featured": False,
    },
    {
        "store_slug": "freshgrocer",
        "category_slug": "produce",
        "name": "Hass Avocado",
        "brand": None,
        "ean": "7890123456803",
        "store_product_id": "FG-004",
        "unit": "unit",
        "regular_price": 499,
        "sale_price": 349,
        "discount_pct": "30.06",
        "is_on_sale": True,
        "is_featured": True,
    },
    {
        "store_slug": "freshgrocer",
        "category_slug": "produce",
        "name": "Organic Spinach 200g",
        "brand": "Green Earth",
        "ean": "7890123456804",
        "store_product_id": "FG-005",
        "unit": "200g",
        "regular_price": 899,
        "sale_price": None,
        "discount_pct": None,
        "is_on_sale": False,
        "is_featured": False,
    },
    {
        "store_slug": "freshgrocer",
        "category_slug": "produce",
        "name": "Red Apples",
        "brand": None,
        "ean": "7890123456805",
        "store_product_id": "FG-006",
        "unit": "1kg",
        "regular_price": 999,
        "sale_price": 799,
        "discount_pct": "20.02",
        "is_on_sale": True,
        "is_featured": False,
    },
    {
        "store_slug": "freshgrocer",
        "category_slug": "bakery",
        "name": "Whole Wheat Bread 500g",
        "brand": "Wickbold",
        "ean": "7890123456806",
        "store_product_id": "FG-007",
        "unit": "500g",
        "regular_price": 1199,
        "sale_price": 899,
        "discount_pct": "25.02",
        "is_on_sale": True,
        "is_featured": True,
    },
    {
        "store_slug": "freshgrocer",
        "category_slug": "dairy",
        "name": "Almond Milk 1L",
        "brand": "AdeS",
        "ean": "7890123456807",
        "store_product_id": "FG-008",
        "unit": "1L",
        "regular_price": 1599,
        "sale_price": 1199,
        "discount_pct": "25.02",
        "is_on_sale": True,
        "is_featured": False,
    },
    {
        "store_slug": "freshgrocer",
        "category_slug": "meat-poultry",
        "name": "Atlantic Salmon Fillet",
        "brand": "OceanCatch",
        "ean": "7890123456808",
        "store_product_id": "FG-009",
        "unit": "500g",
        "regular_price": 5999,
        "sale_price": 4499,
        "discount_pct": "25.00",
        "is_on_sale": True,
        "is_featured": True,
    },
    {
        "store_slug": "freshgrocer",
        "category_slug": "frozen",
        "name": "Vanilla Ice Cream 1.5L",
        "brand": "Haagen-Dazs",
        "ean": "7890123456809",
        "store_product_id": "FG-010",
        "unit": "1.5L",
        "regular_price": 2999,
        "sale_price": 2299,
        "discount_pct": "23.34",
        "is_on_sale": True,
        "is_featured": False,
    },
    {
        "store_slug": "freshgrocer",
        "category_slug": "frozen",
        "name": "Frozen Mixed Berries",
        "brand": "BerryFresh",
        "ean": "7890123456810",
        "store_product_id": "FG-011",
        "unit": "500g",
        "regular_price": 2199,
        "sale_price": None,
        "discount_pct": None,
        "is_on_sale": False,
        "is_featured": False,
    },
    {
        "store_slug": "freshgrocer",
        "category_slug": "pantry",
        "name": "Spaghetti Pasta 500g",
        "brand": "Barilla",
        "ean": "7890123456811",
        "store_product_id": "FG-012",
        "unit": "500g",
        "regular_price": 899,
        "sale_price": 649,
        "discount_pct": "27.81",
        "is_on_sale": True,
        "is_featured": True,
    },
    {
        "store_slug": "freshgrocer",
        "category_slug": "pantry",
        "name": "Coffee Ground 500g",
        "brand": "Pilao",
        "ean": "7890123456812",
        "store_product_id": "FG-013",
        "unit": "500g",
        "regular_price": 2499,
        "sale_price": 1899,
        "discount_pct": "24.01",
        "is_on_sale": True,
        "is_featured": True,
    },
    {
        "store_slug": "freshgrocer",
        "category_slug": "snacks",
        "name": "Dark Chocolate Bar 90g",
        "brand": "Lindt",
        "ean": "7890123456813",
        "store_product_id": "FG-014",
        "unit": "90g",
        "regular_price": 1299,
        "sale_price": 899,
        "discount_pct": "30.79",
        "is_on_sale": True,
        "is_featured": False,
    },
    {
        "store_slug": "freshgrocer",
        "category_slug": "beverages",
        "name": "Red Wine Cabernet 750ml",
        "brand": "Concha y Toro",
        "ean": "7890123456814",
        "store_product_id": "FG-015",
        "unit": "750ml",
        "regular_price": 4499,
        "sale_price": 3499,
        "discount_pct": "22.23",
        "is_on_sale": True,
        "is_featured": True,
    },
    {
        "store_slug": "freshgrocer",
        "category_slug": "personal-care",
        "name": "Shampoo 400ml",
        "brand": "Pantene",
        "ean": "7890123456815",
        "store_product_id": "FG-016",
        "unit": "400ml",
        "regular_price": 2299,
        "sale_price": 1699,
        "discount_pct": "26.10",
        "is_on_sale": True,
        "is_featured": False,
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
                    "email": s["email"],
                    "telephone_1": s["telephone_1"],
                    "telephone_2": s["telephone_2"],
                    "whatsapp": s["whatsapp"],
                    "has_delivery": s["has_delivery"],
                    "has_pickup": s["has_pickup"],
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

            image_url = f"https://picsum.photos/seed/{p['store_product_id']}/400/400"

            product, created = Product.objects.update_or_create(
                store=store,
                store_product_id=p["store_product_id"],
                defaults={
                    "category": category,
                    "name": p["name"],
                    "brand": brand,
                    "ean": p["ean"],
                    "unit": p["unit"],
                    "image_url": image_url,
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

            # Create Post and PostPrices for the post-based feed
            temperature = random.randint(5, 80) if p["is_featured"] else random.randint(-10, 30)
            expires_at = today + timedelta(days=random.randint(3, 10)) if p.get("is_featured") else None
            post, _ = Post.objects.get_or_create(
                product=product,
                store=store,
                defaults={
                    "temperature": temperature,
                    "expires_at": expires_at,
                    "is_active": True,
                },
            )
            PostPrice.objects.get_or_create(
                post=post,
                discount_type="regular",
                defaults={"amount": p["regular_price"], "currency": "BRL"},
            )
            if p.get("sale_price"):
                PostPrice.objects.get_or_create(
                    post=post,
                    discount_type="discounted",
                    defaults={"amount": p["sale_price"], "currency": "BRL"},
                )

        self.stdout.write(self.style.SUCCESS("Done. Dummy data seeded successfully."))
