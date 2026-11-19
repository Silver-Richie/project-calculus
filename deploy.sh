#!/usr/bin/env bash
# Perbarui situs di PythonAnywhere dengan kode terbaru dari GitHub (branch main).
#
# Usage (Bash console PythonAnywhere):
#     cd ~/project-calculus && bash deploy.sh
#
# Mechanism: ambil kode → pasang library baru → ubah struktur database → muat ulang
# kurikulum dari gamification/content → kumpulkan CSS/JS → muat ulang web app.
# Berhenti di langkah pertama yang gagal, sehingga situs lama tetap berjalan.
set -euo pipefail
cd "$(dirname "$0")"

PY="${VIRTUAL_ENV:-$HOME/.virtualenvs/calculus}/bin/python"

echo "1/6 Ambil kode terbaru";       git pull --ff-only origin main
echo "2/6 Pasang library";           "$PY" -m pip install -q -r requirements.txt
echo "3/6 Migrasi database";         "$PY" manage.py migrate --noinput
echo "4/6 Muat kurikulum";           "$PY" manage.py seed_gamification
echo "5/6 Kumpulkan berkas static";  "$PY" manage.py collectstatic --noinput -v 0
echo "6/6 Muat ulang web app"
# Menyentuh berkas WSGI = tombol Reload di tab Web.
touch "/var/www/$(whoami | tr '[:upper:]' '[:lower:]')_pythonanywhere_com_wsgi.py"
echo "Selesai. Buka https://$(whoami | tr '[:upper:]' '[:lower:]').pythonanywhere.com"
