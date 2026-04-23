# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`tabloid-web` is a Django 5.2 web application using Python 3.14. It is managed with `uv` and uses SQLite as the database.

## Commands

All commands assume the virtualenv is active or run via `uv run`.

```bash
# Install dependencies
uv sync

# Run development server
uv run python manage.py runserver

# Apply migrations
uv run python manage.py migrate

# Create migrations after model changes
uv run python manage.py makemigrations

# Run all tests
uv run python manage.py test

# Run tests for a specific app
uv run python manage.py test <app_name>

# Run a single test
uv run python manage.py test <app_name>.tests.TestClass.test_method

# Open Django shell
uv run python manage.py shell
```

## Architecture

This is a freshly scaffolded Django project. The main package is `tabloid_web/`, which holds global settings, URL routing, and WSGI/ASGI entry points. Application-specific logic should be added as Django apps (subdirectories with their own `models.py`, `views.py`, `urls.py`, etc.) and registered in `INSTALLED_APPS` in `tabloid_web/settings.py`.

- **Settings**: `tabloid_web/settings.py` — currently uses SQLite and a hardcoded insecure secret key (dev only)
- **URL root**: `tabloid_web/urls.py` — only the admin route is registered; app URLs should be included here
- **Database**: SQLite at `db.sqlite3` in the project root (dev default)
