# SPECS.md

## Overview

`tabloid-web` is a Django web application that surfaces daily featured product deals from multiple stores. The homepage shows a horizontal product carousel filterable by store, state, and city.

## Stack

### Backend
- **Python** 3.14 (`.python-version`, `pyproject.toml` requires `>=3.14`)
- **Django** 5.2.13
- **Pillow** 12.2+ (image handling)
- **uv** — package manager and task runner (not pip/Poetry)
- **SQLite** with **SpatiaLite** extension (`django.contrib.gis.db.backends.spatialite`, `mod_spatialite`) for geographic queries on store addresses

### Frontend
- **HTMX** 2.0.4 — AJAX partial refresh for store/location filtering (loaded via unpkg CDN in `base.html`)
- **Tailwind CSS** v4.2.4 — styling, built via `@tailwindcss/cli` installed with **Bun** (`package.json` / `bun.lock`). Input: `static/css/tailwind.css`; output: `static/css/output.css` (committed)
- **Swiper.js** v11 — horizontal product carousel, served locally from `static/js/swiper.min.js` + `static/css/swiper.min.css`

## Project Layout

```
tabloid-web/
├── manage.py
├── pyproject.toml          # uv-managed Python dependencies
├── uv.lock
├── package.json            # bun-managed frontend tooling (Tailwind CLI)
├── bun.lock
├── db.sqlite3              # SpatiaLite database
├── tabloid_web/            # project package (settings, urls, wsgi/asgi)
├── catalog/                # products, brands, categories, price snapshots, daily featured
│   ├── models.py
│   ├── services.py         # compute_daily_featured()
│   └── management/commands/seed_dummy_data.py
├── stores/                 # stores and geographic store addresses
│   └── models.py
├── deals/                  # public-facing views (home + HTMX partial)
│   ├── views.py            # HomeView, ProductGridView
│   ├── urls.py
│   └── templates/deals/partials/product_grid.html
├── templates/              # project-level templates
│   ├── base.html
│   ├── index.html
│   └── components/location_selector.html
└── static/
    ├── css/{tailwind.css, output.css, swiper.min.css}
    └── js/swiper.min.js
```

## Django Apps

| App | Purpose |
|---|---|
| `catalog` | Product catalog: `Category`, `Brand`, `Product`, `PriceSnapshot`, `DailyFeatured` |
| `stores` | Stores and geographic store addresses: `Store`, `StoreAddress` (uses `PointField`, SRID 4326) |
| `deals` | Public-facing views (homepage + HTMX partial refresh endpoint) |

Plus `django.contrib.gis` for GIS/SpatiaLite support.

## Data Model

- `stores.Store` — name, slug, `base_url`, `logo_url`, `is_active`
- `stores.StoreAddress` — 1:1 to `Store`, with `city`, `state`, `postal_code`, geographic `location` (PointField)
- `catalog.Category` — self-referential tree
- `catalog.Brand` — name, slug, image
- `catalog.Product` — FK to `Store`, `Category`, `Brand`; `ean`, `store_product_id`, `product_url`, `image_url`, `unit`. Unique per `(store, store_product_id)`
- `catalog.PriceSnapshot` — FK to `Product`; `date`, `regular_price`, `sale_price`, `unit_price`, `discount_pct`, `is_featured`, `is_on_sale`
- `catalog.DailyFeatured` — FK to `PriceSnapshot` and `Store`; `date`, `rank`. Populated by `catalog.services.compute_daily_featured(store, date, top_n=20)` which ranks by `is_featured` then `discount_pct`

## URL Routing

Root URLconf (`tabloid_web/urls.py`) mounts `deals.urls` at `/` and admin at `/admin/`.

| Path | View | Purpose |
|---|---|---|
| `/` | `deals.views.HomeView` | Homepage rendering `templates/index.html` |
| `/products/filter/` | `deals.views.ProductGridView` | HTMX partial returning `deals/partials/product_grid.html` |
| `/admin/` | Django admin | — |

## Filtering Flow

- Filter parameters: `store` (slug), `state`, `city` (query string)
- `HomeView` resolves state/city from query params first, then falls back to cookies (`deals_state`, `deals_city`, 30-day max-age, SameSite=Lax). Cookies are set on every home response.
- `ProductGridView` reads query params only — it is the HTMX swap target and must reflect the URL that HTMX is pushing.
- Store filter buttons use `hx-get` + `hx-target="#product-grid"` + `hx-push-url="true"` to swap just the carousel slides.
- Location (state/city) uses a plain `<form method="get">` that full-reloads the page (simpler than rewiring two linked `<select>`s over HTMX). Client-side JS in `index.html` rebuilds city options when state changes, using a `{{ cities_by_state|json_script:"..." }}` payload.

## Carousel (Swiper + HTMX)

- `#product-swiper` (`.swiper`) wraps `#product-grid` (`.swiper-wrapper`). Each card is a `.swiper-slide` with fixed width (`!w-[200px] sm:!w-[300px]`) to override Swiper's default `width: 100%`.
- Prev/next buttons (`#swiper-prev`, `#swiper-next`) sit **outside** `#product-grid` so they survive HTMX `innerHTML` swaps.
- Swiper configured with `slidesPerView: 'auto'`, `spaceBetween: 16`. On `htmx:afterSwap` targeting `#product-grid`, the existing Swiper is `destroy(true, true)`'d and re-instantiated.

## Template Layering

- `templates/base.html` — loads Swiper CSS first, then Tailwind `output.css` (so Tailwind wins on equal specificity). HTMX loaded in `<head>`. Swiper JS loaded before `{% block extra_scripts %}` at end of body.
- `templates/index.html` — filter bar + carousel + city/state selector init JS + Swiper init JS
- `deals/templates/deals/partials/product_grid.html` — just slide `<a>` elements (no outer wrapper — `#product-grid` already is the `.swiper-wrapper`)

## Tailwind Build

Input `static/css/tailwind.css` uses v4 syntax:
- `@import "tailwindcss";`
- `@source "../../templates";` and `@source "../../deals/templates";` (template discovery)
- `@theme { --color-brand: #e63946; }` (brand color available as `text-brand`, `bg-brand`, etc.)
- `@utility scrollbar-none { … }` (custom utility)
- Plain CSS rules for `.htmx-indicator` opacity transitions

Rebuild commands (via Bun):

```bash
bun install              # install @tailwindcss/cli (first-time or after package.json change)
bun run build:css        # one-shot minified build
bun run watch:css        # rebuild on template changes
```

`output.css` is committed — Django serves it via `staticfiles`.

## Localization

- `LANGUAGE_CODE = 'pt-BR'`, `TIME_ZONE = 'America/Sao_Paulo'`
- `USE_I18N`, `USE_L10N`, `USE_TZ`, `USE_THOUSAND_SEPARATOR` all `True`
- Prices rendered via `{{ value|localize }}` (e.g. `R$1.234,56`)

## Commands

```bash
uv sync                                    # install deps
uv run python manage.py runserver          # dev server
uv run python manage.py migrate
uv run python manage.py makemigrations
uv run python manage.py check
uv run python manage.py test [<app>]
uv run python manage.py seed_dummy_data --clear   # populate demo data
```

## Non-obvious Gotchas

- Scraper code was removed — no `scrapers` module, no `scrape_all`/`scrape_store` commands. Use `seed_dummy_data` for local data.
- SpatiaLite requires `mod_spatialite` installed system-wide; `SPATIALITE_LIBRARY_PATH = 'mod_spatialite'` in settings.
- `SECRET_KEY` in `settings.py` is the insecure dev default and `DEBUG = True` — not production-ready.
- `stores.models.Store` lives in the `stores` app, not `catalog` (historical reason: originally in `catalog`, migrated out).
- Swiper's own CSS sets `.swiper-slide { width: 100% }` — always override with `!w-[...]` Tailwind classes (the `!` adds `!important`).
