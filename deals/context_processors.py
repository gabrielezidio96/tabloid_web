from .cart import Cart
from .models import Notification
from .views import STATE_COOKIE, CITY_COOKIE


VERTICAL_LABELS = {"supermarket": "Mercado", "pharmacy": "Farmácia"}
VERTICAL_BRAND_NAMES = {"supermarket": "Tabloid", "pharmacy": "Tabloid Saúde"}
VERTICAL_BRAND_LETTERS = {"supermarket": "T", "pharmacy": "S"}


def cart(request):
    v = getattr(request, "vertical", None)
    return {"cart_count": len(Cart(request.session, v))}


def notifications(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, read=False).count()
    else:
        count = 0
    return {"unread_notifications_count": count}


def location(request):
    state = request.GET.get("state", request.COOKIES.get(STATE_COOKIE, "")).strip()
    city = request.GET.get("city", request.COOKIES.get(CITY_COOKIE, "")).strip()
    return {"selected_state": state, "selected_city": city}


def vertical(request):
    v = getattr(request, "vertical", "supermarket")
    return {
        "vertical": v,
        "vertical_label": VERTICAL_LABELS.get(v, ""),
        "vertical_brand_name": VERTICAL_BRAND_NAMES.get(v, "Tabloid"),
        "vertical_brand_letter": VERTICAL_BRAND_LETTERS.get(v, "T"),
    }
