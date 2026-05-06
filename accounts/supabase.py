import base64
import hashlib
import secrets
from urllib.parse import urlencode

import requests
from django.conf import settings


SUPPORTED_PROVIDERS = ("google", "facebook")


def generate_pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    return verifier, challenge


def build_authorize_url(provider: str, redirect_uri: str, code_challenge: str, state: str) -> str:
    params = {
        "provider": provider,
        "redirect_to": redirect_uri,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state,
    }
    return f"{settings.SUPABASE_URL}/auth/v1/authorize?{urlencode(params)}"


def exchange_code(code: str, code_verifier: str) -> dict:
    resp = requests.post(
        f"{settings.SUPABASE_URL}/auth/v1/token",
        params={"grant_type": "pkce"},
        headers={
            "apikey": settings.SUPABASE_ANON_KEY,
            "Content-Type": "application/json",
        },
        json={"auth_code": code, "code_verifier": code_verifier},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_user(access_token: str) -> dict:
    resp = requests.get(
        f"{settings.SUPABASE_URL}/auth/v1/user",
        headers={
            "apikey": settings.SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {access_token}",
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()
