VERTICAL_COOKIE = "tabloid_vertical"
VERTICAL_COOKIE_MAX_AGE = 60 * 60 * 24 * 365
VALID_VERTICALS = {"supermarket", "pharmacy"}
DEFAULT_VERTICAL = "supermarket"


class VerticalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        toggle = request.GET.get("set_vertical")
        if toggle in VALID_VERTICALS:
            request.vertical = toggle
            should_persist = True
        else:
            cookie = request.COOKIES.get(VERTICAL_COOKIE, DEFAULT_VERTICAL)
            request.vertical = cookie if cookie in VALID_VERTICALS else DEFAULT_VERTICAL
            should_persist = False

        response = self.get_response(request)

        if should_persist:
            response.set_cookie(
                VERTICAL_COOKIE,
                request.vertical,
                max_age=VERTICAL_COOKIE_MAX_AGE,
                samesite="Lax",
            )
        return response
