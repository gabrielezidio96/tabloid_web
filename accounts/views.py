import secrets

from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from . import supabase


SESSION_KEY = "sb_oauth"


def login(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get("next") or "deals:home")
    return render(
        request,
        "accounts/login.html",
        {"next": request.GET.get("next", "")},
    )


@require_http_methods(["GET"])
def oauth_start(request, provider: str):
    if provider not in supabase.SUPPORTED_PROVIDERS:
        return HttpResponseBadRequest("Unsupported provider")

    verifier, challenge = supabase.generate_pkce_pair()
    state = secrets.token_urlsafe(32)
    request.session[SESSION_KEY] = {
        "verifier": verifier,
        "state": state,
        "next": request.GET.get("next", ""),
    }

    callback_url = request.build_absolute_uri(reverse("accounts:oauth-callback"))
    return redirect(supabase.build_authorize_url(provider, callback_url, challenge, state))


@require_http_methods(["GET"])
def oauth_callback(request):
    payload = request.session.pop(SESSION_KEY, None)
    error = request.GET.get("error_description") or request.GET.get("error")
    code = request.GET.get("code")
    state = request.GET.get("state")

    if error:
        messages.error(request, f"Falha no login: {error}")
        return redirect("accounts:login")

    if not payload or not code or state != payload.get("state"):
        messages.error(request, "Sessão de login inválida. Tente novamente.")
        return redirect("accounts:login")

    try:
        tokens = supabase.exchange_code(code, payload["verifier"])
        sb_user = supabase.fetch_user(tokens["access_token"])
    except Exception:
        messages.error(request, "Não foi possível autenticar com o provedor.")
        return redirect("accounts:login")

    email = (sb_user.get("email") or "").lower()
    if not email:
        messages.error(request, "Provedor não retornou e-mail.")
        return redirect("accounts:login")

    metadata = sb_user.get("user_metadata") or {}
    full_name = metadata.get("full_name") or metadata.get("name") or ""
    first_name, _, last_name = full_name.partition(" ")

    User = get_user_model()
    user, _ = User.objects.update_or_create(
        username=email,
        defaults={
            "email": email,
            "first_name": first_name[:150],
            "last_name": last_name[:150],
        },
    )
    auth.login(request, user)

    return redirect(payload.get("next") or settings.LOGIN_REDIRECT_URL)


@require_POST
def logout(request):
    auth.logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)
