from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.http import HttpResponseBadRequest, JsonResponse
from django.views import View

from stores.models import StoreAddress

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
