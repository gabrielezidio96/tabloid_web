from .cart import Cart
from .models import Notification
from .views import STATE_COOKIE, CITY_COOKIE


def cart(request):
    return {"cart_count": len(Cart(request.session))}


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
