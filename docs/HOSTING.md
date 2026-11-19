# Hosting di PythonAnywhere (akun gratis)

Alur: **laptop → GitHub (`main`) → PythonAnywhere**. Kode tidak pernah diunggah manual;
server selalu mengambil `main` lewat `git pull`. Rahasia hanya ada di `.env` server.

Ganti `USERNAME` di bawah dengan username PythonAnywhere (alamat situs: `https://USERNAME.pythonanywhere.com`).

## A. Pemasangan pertama (sekali saja)

1. **Database** — tidak perlu disiapkan: akun gratis memakai SQLite (`db.sqlite3` di folder proyek,
   dibuat otomatis saat `migrate`; tidak ikut git). Akun gratis baru (sejak 2026) tidak mendapat MySQL.
2. **Kode** — tab *Consoles* → *Bash*:
   ```bash
   git clone https://github.com/Silver-Richie/project-calculus.git
   cd project-calculus
   mkvirtualenv calculus --python=python3.13
   pip install -r requirements.txt
   ```
3. **Rahasia** — `cp .env.example .env` lalu `nano .env`, isi semua nilai bagian server
   (`PRODUCTION=True`, `SECRET_KEY`, `ALLOWED_HOSTS`, `DUEL_ENABLED=False`, `GOOGLE_*`).
   Buat SECRET_KEY: `python -c "import secrets; print(secrets.token_urlsafe(50))"`.
4. **Isi database** — `python manage.py migrate && python manage.py seed_gamification`
   lalu `python manage.py createsuperuser` (akun admin) dan `python manage.py collectstatic --noinput`.
5. **Web app** — tab *Web* → *Add a new web app* → *Manual configuration* → Python 3.13.
   - *Virtualenv*: `/home/USERNAME/.virtualenvs/calculus`
   - *Source code*: `/home/USERNAME/project-calculus`
   - *Static files*: URL `/static/` → Directory `/home/USERNAME/project-calculus/staticfiles`
   - *Force HTTPS*: aktifkan
   - Buka *WSGI configuration file*, hapus seluruh isinya, ganti dengan:
     ```python
     import os, sys
     path = '/home/USERNAME/project-calculus'
     if path not in sys.path:
         sys.path.insert(0, path)
     os.environ['DJANGO_SETTINGS_MODULE'] = 'project_calculus.settings'
     from dotenv import load_dotenv
     load_dotenv(os.path.join(path, '.env'))
     from django.core.wsgi import get_wsgi_application
     application = get_wsgi_application()
     ```
   - Klik **Reload**.
6. **Google** — di Google Cloud Console (OAuth client yang sama), tambahkan redirect URI
   `https://USERNAME.pythonanywhere.com/accounts/google/login/callback/`, dan pada
   *OAuth consent screen* pilih **Publish app** agar semua akun Google bisa masuk.

## B. Setiap update

Di laptop: kerjakan di branch → merge ke `main` lewat PR → push. Lalu di Bash console PythonAnywhere:

```bash
cd ~/project-calculus && workon calculus && bash deploy.sh
```

`deploy.sh` menjalankan: git pull → pip install → migrate → seed_gamification → collectstatic → reload.

## Catatan

- **Akun gratis wajib diperpanjang**: tab *Web* → *Run until 3 months from today*, minimal tiap 3 bulan,
  atau situs dimatikan.
- **Duel** dimatikan (`DUEL_ENABLED=False`): WebSocket butuh server ASGI. Tombolnya tampil "Segera hadir".
- **Cadangan data**: semua akun & progres ada di `~/project-calculus/db.sqlite3`. Unduh berkas itu
  sesekali dari tab *Files*. Jangan pernah menghapusnya.
- **Error**: lihat *Error log* di tab *Web* (`USERNAME.pythonanywhere.com.error.log`).
