from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.decorators.http import require_POST

from stores.models import StoreAddress

from .middleware import (
    VALID_VERTICALS,
    VERTICAL_COOKIE,
    VERTICAL_COOKIE_MAX_AGE,
)


@require_POST
def switch_vertical(request, vertical):
    if vertical not in VALID_VERTICALS:
        return HttpResponseBadRequest("invalid vertical")
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
    if not next_url.startswith("/") or next_url.startswith("//"):
        next_url = "/"
    response = redirect(next_url)
    response.set_cookie(
        VERTICAL_COOKIE,
        vertical,
        max_age=VERTICAL_COOKIE_MAX_AGE,
        samesite="Lax",
    )
    return response

class ClosestLocationView(View):
    def get(self, request):
        try:
            lat = float(request.GET["lat"])
            lng = float(request.GET["lng"])
        except (KeyError, TypeError, ValueError):
            return HttpResponseBadRequest("lat and lng query params are required and must be numeric")

        user_point = Point(lng, lat, srid=4326)
        closest = (
            StoreAddress.objects
            .annotate(distance=Distance("location", user_point))
            .order_by("distance")
            .values("state", "city")
            .first()
        )
        return JsonResponse(closest or {"state": "", "city": ""})
