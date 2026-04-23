from collections import defaultdict

from django.utils import timezone
from django.views.generic import TemplateView

from catalog.models import DailyFeatured
from stores.models import Store, StoreAddress


STATE_COOKIE = "deals_state"
CITY_COOKIE = "deals_city"
FILTER_COOKIE_MAX_AGE = 60 * 60 * 24 * 30


def _get_featured(store_slug: str, state: str, city: str, today):
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


def _build_location_filters(selected_state: str):
    states = list(
        StoreAddress.objects.order_by("state")
        .values_list("state", flat=True)
        .distinct()
    )
    addresses = StoreAddress.objects.values("state", "city").order_by("state", "city").distinct()
    cities_by_state = defaultdict(list)
    for address in addresses:
        cities_by_state[address["state"]].append(address["city"])

    if selected_state:
        cities = cities_by_state.get(selected_state, [])
    else:
        cities = []
    return states, cities, dict(cities_by_state)


def _resolve_filter(request, param_name: str, cookie_name: str) -> str:
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
        states, cities, cities_by_state = _build_location_filters(selected_state)
        if selected_city and selected_city not in cities:
            selected_city = ""

        ctx["stores"] = Store.objects.filter(is_active=True)
        ctx["featured"] = _get_featured(store_slug, selected_state, selected_city, today)
        ctx["selected_store"] = store_slug
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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()
        store_slug = self.request.GET.get("store", "")
        selected_state = self.request.GET.get("state", "")
        selected_city = self.request.GET.get("city", "")

        ctx["featured"] = _get_featured(store_slug, selected_state, selected_city, today)
        ctx["selected_store"] = store_slug
        return ctx