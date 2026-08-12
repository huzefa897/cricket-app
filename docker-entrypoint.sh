#!/bin/sh
# Apply migrations against the mounted volume DB, then run the given command
# (gunicorn by default). Keeps the image declarative — no manual migrate step.
set -e

mkdir -p "$(dirname "${DJANGO_DB_PATH:-/app/data/db.sqlite3}")"
python manage.py migrate --noinput

exec "$@"
