# AGENTS.md

## Fast Facts
- This is a single Django project (`tabloid_web`) managed with `uv` (not Poetry/pip-tools).
- Python requirement is `>=3.14` (`pyproject.toml`).
- Database is SQLite at `db.sqlite3`.
- Installed local apps are `catalog` and `deals` (`tabloid_web/settings.py`).

## Commands (source of truth)
- Sync deps: `uv sync`
- Run server: `uv run python manage.py runserver`
- System check: `uv run python manage.py check`
- Apply migrations: `uv run python manage.py migrate`
- Create migrations after model changes: `uv run python manage.py makemigrations`
- Run all tests: `uv run python manage.py test`
- Run one app's tests: `uv run python manage.py test <app_name>`
- Run one test: `uv run python manage.py test <app_name>.tests.TestClass.test_method`
- Seed demo data: `uv run python manage.py seed_dummy_data --clear`

## Project Wiring
- Root URL config mounts `deals.urls` at `/` and admin at `/admin/` (`tabloid_web/urls.py`).
- Deals homepage is `deals.views.HomeView`; HTMX partial refresh endpoint is `deals.views.ProductGridView` at `/products/filter/`.
- Featured deals rendered on the homepage come from `catalog.DailyFeatured`, populated by `catalog.services.compute_daily_featured(...)`.

## Repo-Specific Gotchas
- Scraper code/commands were removed; do not rely on `scrapers` module or `manage.py scrape_all`/`scrape_store`.
- To get local data for UI work, use `seed_dummy_data` instead of scraper workflows.
- `README.md` is currently empty; prefer `CLAUDE.md` plus Django settings/URLs/models as the reliable context.
