from datetime import date

from stores.models import Store

from .models import DailyFeatured, PriceSnapshot


def compute_daily_featured(store: Store, target_date: date, top_n: int = 20) -> int:
    """
    Populate DailyFeatured for a store+date.
    Ranking: featured items first, then by discount_pct descending.
    Returns the number of rows created.
    """
    DailyFeatured.objects.filter(store=store, date=target_date).delete()

    snapshots = list(
        PriceSnapshot.objects.filter(product__store=store, date=target_date)
        .select_related("product")
        .order_by("-is_featured", "-discount_pct")[:top_n]
    )

    DailyFeatured.objects.bulk_create(
        [
            DailyFeatured(date=target_date, snapshot=s, store=store, rank=i + 1)
            for i, s in enumerate(snapshots)
        ]
    )

    return len(snapshots)
