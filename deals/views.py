from collections import defaultdict
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Prefetch
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView

from catalog.models import DailyFeatured, PriceSnapshot, Product
from stores.models import Store, StoreAddress

from .cart import Cart, PRICE_KEYS, DEFAULT_PRICE_KEY
from .models import Notification, Post, PostVote, SavedList, SavedListItem


STATE_COOKIE = "deals_state"
CITY_COOKIE = "deals_city"
FILTER_COOKIE_MAX_AGE = 60 * 60 * 24 * 30

PRICE_KEY_LABELS = {
    "priceRegular": "Regular",
    "priceDiscounted": "Oferta",
    "priceApp": "App",
    "priceCreditCardClub": "Clube",
}


def _snapshot_value(snapshot, price_key):
    if snapshot is None:
        return None
    if price_key == "priceRegular":
        return snapshot.regular_price
    if price_key == "priceDiscounted":
        return snapshot.sale_price
    if price_key == "priceApp":
        return snapshot.price_app
    if price_key == "priceCreditCardClub":
        return snapshot.price_credit_card_club
    return None


def _available_prices(snapshot):
    if snapshot is None:
        return []
    return [
        (key, PRICE_KEY_LABELS[key], _snapshot_value(snapshot, key))
        for key in PRICE_KEYS
        if _snapshot_value(snapshot, key) is not None
    ]


def _get_featured(store_slug, state, city, today):
    qs = (
        DailyFeatured.objects.filter(date=today)
        .select_related(
            "snapshot__product__store",
            "snapshot__product__category",
            "store__address",
            "store",
        )
        .order_by("rank")
    )
    if store_slug:
        qs = qs.filter(store__slug=store_slug)
    if state:
        qs = qs.filter(store__address__state=state)
    if city:
        qs = qs.filter(store__address__city=city)
    return qs


_SORT_ORDERS = {
    "featured": ["-snapshots__is_featured", "-snapshots__discount_pct", "name"],
    "recent":   ["-snapshots__scraped_at", "name"],
    "trending": ["-snapshots__discount_pct", "name"],
    "cheapest": ["snapshots__sale_price", "snapshots__regular_price", "name"],
}
VALID_SORTS = set(_SORT_ORDERS)


def _get_products(store_slug, state, city, today, sort="featured"):
    order = _SORT_ORDERS.get(sort, _SORT_ORDERS["featured"])
    today_snapshots = PriceSnapshot.objects.filter(date=today)
    qs = (
        Product.objects.select_related("store", "category", "brand")
        .filter(snapshots__date=today)
        .prefetch_related(
            Prefetch("snapshots", queryset=today_snapshots, to_attr="today_snapshots")
        )
        .distinct()
        .order_by(*order)
    )
    if store_slug:
        qs = qs.filter(store__slug=store_slug)
    if state:
        qs = qs.filter(store__address__state=state)
    if city:
        qs = qs.filter(store__address__city=city)
    return qs


def _build_location_filters(selected_state):
    states = list(
        StoreAddress.objects.order_by("state").values_list("state", flat=True).distinct()
    )
    addresses = StoreAddress.objects.values("state", "city").order_by("state", "city").distinct()
    cities_by_state = defaultdict(list)
    for address in addresses:
        cities_by_state[address["state"]].append(address["city"])
    cities = cities_by_state.get(selected_state, []) if selected_state else []
    return states, cities, dict(cities_by_state)


def _resolve_filter(request, param_name, cookie_name):
    if param_name in request.GET:
        return request.GET.get(param_name, "").strip()
    return request.COOKIES.get(cookie_name, "").strip()


class HomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()
        store_slug = self.request.GET.get("store", "")
        selected_state = _resolve_filter(self.request, "state", STATE_COOKIE)
        selected_city = _resolve_filter(self.request, "city", CITY_COOKIE)
        sort = self.request.GET.get("sort", "featured")
        if sort not in VALID_SORTS:
            sort = "featured"
        states, cities, cities_by_state = _build_location_filters(selected_state)
        if selected_city and selected_city not in cities:
            selected_city = ""

        ctx["stores"] = Store.objects.filter(is_active=True)
        ctx["featured"] = _get_featured(store_slug, selected_state, selected_city, today)
        ctx["products"] = _get_products(store_slug, selected_state, selected_city, today, sort)
        ctx["selected_store"] = store_slug
        ctx["selected_sort"] = sort
        ctx["states"] = states
        ctx["cities"] = cities
        ctx["cities_by_state"] = cities_by_state
        ctx["selected_state"] = selected_state
        ctx["selected_city"] = selected_city
        ctx["today"] = today
        return ctx

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response.set_cookie(
            STATE_COOKIE,
            context.get("selected_state", ""),
            max_age=FILTER_COOKIE_MAX_AGE,
            samesite="Lax",
        )
        response.set_cookie(
            CITY_COOKIE,
            context.get("selected_city", ""),
            max_age=FILTER_COOKIE_MAX_AGE,
            samesite="Lax",
        )
        return response


class ProductGridView(TemplateView):
    template_name = "deals/partials/product_grid.html"

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request") != "true":
            url = reverse("deals:home")
            qs = request.META.get("QUERY_STRING", "")
            if qs:
                url = f"{url}?{qs}"
            return redirect(url)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()
        store_slug = self.request.GET.get("store", "")
        selected_state = self.request.GET.get("state", "")
        selected_city = self.request.GET.get("city", "")
        ctx["featured"] = _get_featured(store_slug, selected_state, selected_city, today)
        ctx["selected_store"] = store_slug
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = "deals/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.select_related("store", "brand", "category")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.object
        snapshot = product.snapshots.order_by("-date", "-scraped_at").first()
        ctx["latest_snapshot"] = snapshot
        ctx["price_history"] = product.snapshots.order_by("-date")[:10]
        ctx["price_rows"] = self._build_price_rows(snapshot) if snapshot else []
        return ctx

    def _build_price_rows(self, snapshot):
        configs = [
            ("regular", "Preço normal", "tag", "#9ca3af", "#e5e7eb", snapshot.regular_price),
            ("discounted", "Oferta", "percent", "#ef4444", "#fca5a5", snapshot.sale_price),
            ("app", "Preço App", "mobile-screen", "#f97316", "#fdba74", snapshot.price_app),
            ("club", "Clube de crédito", "credit-card", "#3b82f6", "#93c5fd", snapshot.price_credit_card_club),
        ]
        rows = []
        for row_id, label, icon, icon_color, accent, value in configs:
            if value is None:
                continue
            rows.append({
                "id": row_id,
                "label": label,
                "icon": icon,
                "icon_color": icon_color,
                "accent_color": accent,
                "value": value,
            })
        if not rows:
            return rows
        best = min(r["value"] for r in rows)
        regular = snapshot.regular_price
        for r in rows:
            r["is_best"] = r["value"] == best and len(rows) > 1
            r["is_regular_with_better"] = r["id"] == "regular" and best < r["value"]
            if r["id"] != "regular" and regular and r["value"] < regular:
                r["savings"] = int(round((regular - r["value"]) / regular * 100))
            else:
                r["savings"] = None
        return rows


def _safe_next(request, fallback_url):
    candidate = request.POST.get("next") or request.GET.get("next") or ""
    if candidate.startswith("/") and not candidate.startswith("//"):
        return candidate
    return fallback_url


def _build_cart_rows(cart):
    cart_items = cart.items()
    if not cart_items:
        return [], Decimal("0")

    ids = [int(pid) for pid in cart_items]
    latest_snapshots = PriceSnapshot.objects.order_by("-date", "-scraped_at")
    products = (
        Product.objects.filter(id__in=ids)
        .select_related("store", "brand")
        .prefetch_related(Prefetch("snapshots", queryset=latest_snapshots, to_attr="recent_snapshots"))
    )

    rows = []
    total = Decimal("0")
    for product in products:
        entry = cart_items.get(str(product.id), {"qty": 0, "price_key": DEFAULT_PRICE_KEY})
        qty = entry["qty"]
        price_key = entry["price_key"]
        snapshot = product.recent_snapshots[0] if product.recent_snapshots else None
        unit_price = _snapshot_value(snapshot, price_key)
        if unit_price is None:
            unit_price = _snapshot_value(snapshot, DEFAULT_PRICE_KEY) or Decimal("0")
            price_key = DEFAULT_PRICE_KEY
        line_total = unit_price * qty
        total += line_total
        rows.append({
            "product": product,
            "qty": qty,
            "snapshot": snapshot,
            "unit_price": unit_price,
            "line_total": line_total,
            "selected_price_key": price_key,
            "available_prices": _available_prices(snapshot),
        })
    rows.sort(key=lambda r: r["product"].name.lower())
    return rows, total


def _group_rows_by_store(rows):
    groups_map = {}
    for row in rows:
        title = row["product"].store.name if row["product"].store else "Outros"
        groups_map.setdefault(title, []).append(row)
    groups = []
    for title, group_rows in groups_map.items():
        subtotal = sum((r["line_total"] for r in group_rows), Decimal("0"))
        groups.append({"title": title, "rows": group_rows, "subtotal": subtotal})
    return groups


class CartView(TemplateView):
    template_name = "deals/cart.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cart = Cart(self.request.session)
        rows, total = _build_cart_rows(cart)
        ctx["rows"] = rows
        ctx["total"] = total
        ctx["item_count"] = len(rows)
        ctx["store_groups"] = _group_rows_by_store(rows)
        return ctx


@require_POST
def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        qty = int(request.POST.get("qty", 1))
    except (TypeError, ValueError):
        qty = 1
    qty = max(1, qty)
    Cart(request.session).add(product.id, qty)
    return redirect(_safe_next(request, reverse("deals:cart")))


@require_POST
def cart_update(request, pk):
    get_object_or_404(Product, pk=pk)
    try:
        qty = int(request.POST.get("qty", 0))
    except (TypeError, ValueError):
        qty = 0
    Cart(request.session).set_qty(pk, qty)
    return redirect(_safe_next(request, reverse("deals:cart")))


@require_POST
def cart_remove(request, pk):
    Cart(request.session).remove(pk)
    return redirect(_safe_next(request, reverse("deals:cart")))


@require_POST
def cart_clear(request):
    Cart(request.session).clear()
    return redirect(reverse("deals:cart"))


@require_POST
def cart_set_price(request, pk):
    price_key = request.POST.get("price_key", DEFAULT_PRICE_KEY)
    Cart(request.session).set_price_key(pk, price_key)
    return redirect(_safe_next(request, reverse("deals:cart")))


@require_POST
def cart_save(request):
    if not request.user.is_authenticated:
        return redirect(reverse("deals:cart"))
    cart = Cart(request.session)
    rows, _ = _build_cart_rows(cart)
    if not rows:
        return redirect(reverse("deals:cart"))
    name = request.POST.get("name", "").strip() or f"Lista {timezone.localdate():%d/%m/%Y}"
    saved = SavedList.objects.create(user=request.user, name=name)
    for row in rows:
        SavedListItem.objects.create(
            saved_list=saved,
            product=row["product"],
            quantity=row["qty"],
            selected_price_key=row["selected_price_key"],
        )
    cart.clear()
    return redirect(reverse("deals:saved-list-list"))


class NotificationListView(TemplateView):
    template_name = "deals/notifications.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            qs = Notification.objects.filter(user=self.request.user)
            ctx["notifications"] = list(qs)
            ctx["unread_count"] = qs.filter(read=False).count()
        else:
            ctx["notifications"] = []
            ctx["unread_count"] = 0
        return ctx


@require_POST
@login_required
def notification_mark(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.read = True
    notification.save(update_fields=["read"])
    return redirect(reverse("deals:notification-list"))


@require_POST
@login_required
def notification_mark_all(request):
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return redirect(reverse("deals:notification-list"))


class SavedListListView(TemplateView):
    template_name = "deals/saved_lists.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            ctx["lists"] = []
            return ctx
        lists = SavedList.objects.filter(user=self.request.user).prefetch_related("items__product")
        latest_snapshots = PriceSnapshot.objects.order_by("-date", "-scraped_at")
        annotated = []
        for saved in lists:
            total = Decimal("0")
            for item in saved.items.all():
                product = item.product
                snapshot = product.snapshots.order_by("-date", "-scraped_at").first() if not hasattr(product, "_cached_snap") else product._cached_snap
                value = _snapshot_value(snapshot, item.selected_price_key) or Decimal("0")
                total += value * item.quantity
            annotated.append({
                "pk": saved.pk,
                "name": saved.name,
                "created_at": saved.created_at,
                "item_count": saved.items.count(),
                "total": total,
            })
        ctx["lists"] = annotated
        return ctx


@method_decorator(login_required, name="dispatch")
class SavedListDetailView(DetailView):
    model = SavedList
    template_name = "deals/saved_list_detail.html"
    context_object_name = "saved_list"

    def get_queryset(self):
        return SavedList.objects.filter(user=self.request.user).prefetch_related(
            "items__product__store",
            "items__product__brand",
            "items__product__snapshots",
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        rows = []
        total = Decimal("0")
        for item in self.object.items.all():
            product = item.product
            snapshot = product.snapshots.order_by("-date", "-scraped_at").first()
            unit_price = _snapshot_value(snapshot, item.selected_price_key) or Decimal("0")
            line_total = unit_price * item.quantity
            total += line_total
            rows.append({
                "product": product,
                "qty": item.quantity,
                "unit_price": unit_price,
                "line_total": line_total,
                "price_label": PRICE_KEY_LABELS.get(item.selected_price_key, "Regular"),
            })
        ctx["store_groups"] = _group_rows_by_store(rows)
        ctx["total"] = total
        return ctx


@require_POST
@login_required
def saved_list_delete(request, pk):
    SavedList.objects.filter(user=request.user, pk=pk).delete()
    return redirect(reverse("deals:saved-list-list"))


@require_POST
@login_required
def saved_list_load(request, pk):
    saved = get_object_or_404(SavedList, user=request.user, pk=pk)
    cart = Cart(request.session)
    for item in saved.items.all():
        cart.add(item.product_id, item.quantity)
        cart.set_price_key(item.product_id, item.selected_price_key)
    return redirect(reverse("deals:cart"))


class StoreListView(ListView):
    template_name = "deals/store_list.html"
    context_object_name = "stores"

    def get_queryset(self):
        return Store.objects.filter(is_active=True).order_by("name")


class StoreDetailView(DetailView):
    model = Store
    template_name = "deals/store.html"
    context_object_name = "store"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()
        today_snapshots = PriceSnapshot.objects.filter(date=today)
        ctx["products"] = (
            Product.objects.filter(store=self.object, snapshots__date=today)
            .select_related("brand", "store")
            .prefetch_related(
                Prefetch("snapshots", queryset=today_snapshots, to_attr="today_snapshots")
            )
            .distinct()
            .order_by("name")
        )
        return ctx


# ---------------------------------------------------------------------------
# Post feed
# ---------------------------------------------------------------------------

SESSION_POST_VOTES_KEY = "post_votes"

_TEMP_HOT_THRESHOLD = 1
_TEMP_COLD_THRESHOLD = -1


def get_expiry_info(expires_at):
    """Python equivalent of getExpiryInfo() from the mobile app."""
    if expires_at is None:
        return None
    today = timezone.localdate()
    delta = (expires_at - today).days
    if delta < 0:
        return None
    if delta == 0:
        return {"label": "hoje", "is_today": True}
    if delta == 1:
        return {"label": "amanhã", "is_today": False}
    return {"label": f"em {delta} dias", "is_today": False}


def get_relative_time(posted_at):
    """Python equivalent of getRelativeTime() from the mobile app."""
    diff = int((timezone.now() - posted_at).total_seconds())
    if diff < 60:
        return f"{diff} s"
    if diff < 3600:
        return f"{diff // 60} min"
    if diff < 86400:
        return f"{diff // 3600} h"
    return f"{diff // 86400} d"


def _get_user_post_vote(request, post_id):
    if request.user.is_authenticated:
        return (
            PostVote.objects.filter(post_id=post_id, user=request.user)
            .values_list("direction", flat=True)
            .first()
        )
    return request.session.get(SESSION_POST_VOTES_KEY, {}).get(str(post_id))


def _post_best_price(prices):
    if not prices:
        return None
    return min(p.amount for p in prices)


def _post_regular_price(prices):
    for p in prices:
        if p.discount_type == "regular":
            return p.amount
    return None


def _build_post_row(post, user_vote):
    prices = list(post.prices.all())
    best_price = _post_best_price(prices)
    regular_price = _post_regular_price(prices)
    has_discount = regular_price is not None and best_price is not None and best_price < regular_price
    discount_pct = None
    if has_discount:
        discount_pct = int(round((regular_price - best_price) / regular_price * 100))
    temp = post.temperature
    if temp >= _TEMP_HOT_THRESHOLD:
        temp_class = "hot"
    elif temp <= _TEMP_COLD_THRESHOLD:
        temp_class = "cold"
    else:
        temp_class = "neutral"
    return {
        "post": post,
        "product": post.product,
        "store_name": post.store.name,
        "prices": prices,
        "best_price": best_price,
        "regular_price": regular_price,
        "has_discount": has_discount,
        "discount_pct": discount_pct,
        "expiry_info": get_expiry_info(post.expires_at),
        "relative_time": get_relative_time(post.posted_at),
        "temperature": post.temperature,
        "user_vote": user_vote,
        "temp_class": temp_class,
    }


VALID_POST_SORTS = {"recent", "trending", "expiring"}

_POST_SORT_ORDERS = {
    "recent": ["-posted_at"],
    "trending": ["-temperature", "-posted_at"],
    "expiring": ["expires_at", "-posted_at"],
}


class PostListView(TemplateView):
    template_name = "deals/post_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        sort = self.request.GET.get("sort", "recent")
        if sort not in VALID_POST_SORTS:
            sort = "recent"
        store_slug = self.request.GET.get("store", "")
        order = _POST_SORT_ORDERS[sort]
        qs = (
            Post.objects.filter(is_active=True)
            .select_related("product__brand", "store")
            .prefetch_related("prices")
            .order_by(*order)
        )
        if store_slug:
            qs = qs.filter(store__slug=store_slug)
        session_votes = self.request.session.get(SESSION_POST_VOTES_KEY, {})
        rows = []
        for post in qs:
            if self.request.user.is_authenticated:
                user_vote = (
                    PostVote.objects.filter(post=post, user=self.request.user)
                    .values_list("direction", flat=True)
                    .first()
                )
            else:
                user_vote = session_votes.get(str(post.pk))
            rows.append(_build_post_row(post, user_vote))
        ctx["rows"] = rows
        ctx["selected_sort"] = sort
        ctx["stores"] = Store.objects.filter(is_active=True)
        ctx["selected_store"] = store_slug
        return ctx


class PostDetailView(DetailView):
    model = Post
    template_name = "deals/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return (
            Post.objects.filter(is_active=True)
            .select_related("product__brand", "product__category", "store")
            .prefetch_related("prices")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user_vote = _get_user_post_vote(self.request, self.object.pk)
        ctx.update(_build_post_row(self.object, user_vote))
        return ctx


@require_POST
@transaction.atomic
def post_vote(request, pk):
    post = get_object_or_404(Post.objects.select_for_update(), pk=pk, is_active=True)
    direction = request.POST.get("direction", "")
    if direction not in ("up", "down"):
        return redirect(_safe_next(request, reverse("deals:post-list")))

    delta = 1 if direction == "up" else -1

    if request.user.is_authenticated:
        existing = PostVote.objects.filter(post=post, user=request.user).first()
        if existing:
            if existing.direction == direction:
                post.temperature = F("temperature") - delta
                existing.delete()
            else:
                post.temperature = F("temperature") + delta * 2
                existing.direction = direction
                existing.save(update_fields=["direction"])
        else:
            PostVote.objects.create(post=post, user=request.user, direction=direction)
            post.temperature = F("temperature") + delta
        post.save(update_fields=["temperature"])
    else:
        votes = request.session.get(SESSION_POST_VOTES_KEY, {})
        key = str(pk)
        existing = votes.get(key)
        if existing == direction:
            post.temperature = F("temperature") - delta
            votes.pop(key)
        elif existing:
            post.temperature = F("temperature") + delta * 2
            votes[key] = direction
        else:
            post.temperature = F("temperature") + delta
            votes[key] = direction
        request.session[SESSION_POST_VOTES_KEY] = votes
        post.save(update_fields=["temperature"])

    return redirect(_safe_next(request, reverse("deals:post-list")))
