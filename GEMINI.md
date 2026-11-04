# Antigravity Workspace: project-calculus

## Overview
- **Project**: `project-calculus`
- **Framework**: Django 5.2 (Python 3.14)
- **Database**: SQLite3 (`db.sqlite3`) for local development, PostgreSQL (`psycopg2-binary`) for production.
- **Environment**: Virtual environment located at `./env` (`env\Scripts\python.exe` on Windows).

## Environment & Commands
Always execute Python commands using the workspace virtual environment:
- **Python**: `.\env\Scripts\python.exe`
- **Run Server**: `.\env\Scripts\python.exe manage.py runserver 8000`
- **Check Project**: `.\env\Scripts\python.exe manage.py check`
- **Run Tests**: `.\env\Scripts\python.exe manage.py test`
- **Make Migrations**: `.\env\Scripts\python.exe manage.py makemigrations`
- **Apply Migrations**: `.\env\Scripts\python.exe manage.py migrate`
- **Install Packages**: `.\env\Scripts\pip.exe install -r requirements.txt`
- **Seed Curriculum Content**: `.\env\Scripts\python.exe manage.py seed_gamification` (materi & soal per berkas PDF di `gamification/content/`, lihat README di folder itu)

## Project Architecture
- `manage.py`: Django entrypoint.
- `project_calculus/`: Project configuration root.
  - `settings.py`: Main settings with `dotenv` support.
  - `urls.py`: Main URL routing.
  - `views.py`: Application view handlers.
  - `wsgi.py` / `asgi.py`: Web deployment interfaces.
- `templates/`: HTML templates.
- `static/`: Static files (`css/`, `img/`, etc.).
- `env/`: Isolated virtual environment (excluded from git).
- `.env`: Local environment configurations.

## Antigravity Agent Guidelines
1. **Always Use Workspace Virtualenv**: Use `.\env\Scripts\python.exe` or `.\env\Scripts\pip.exe` to avoid interfering with system Python.
2. **Settings & Secrets**: Use `.env` for secrets and environment-specific toggles; do not hardcode production keys into code.
3. **Database Integrity**: Run migrations before testing database changes; never delete `db.sqlite3` without confirmation.
4. **Static & Templates**: Store templates in `templates/` and styling in `static/css/`. Ensure `{% load static %}` is used appropriately.
