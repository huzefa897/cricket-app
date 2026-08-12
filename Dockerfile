# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# Howzatt — single-image build.
#   Stage 1 (node)   : build the Vue SPA -> apps/web/dist
#   Stage 2 (python) : run Django (gunicorn), which serves /api AND the SPA
# ---------------------------------------------------------------------------

# --- Stage 1: build the frontend ------------------------------------------
FROM node:20-slim AS frontend
WORKDIR /repo

# corepack picks up the pnpm version pinned in the root package.json.
RUN corepack enable

# Workspace manifests + the committed lockfile first (cache layer). Installing
# with --frozen-lockfile guarantees the exact dependency graph we tested — a new
# semver-compatible release can't silently change the field image on a rebuild.
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY apps/web/package.json apps/web/
RUN pnpm install --frozen-lockfile --filter web

# Then the source, and build.
COPY apps/web/ apps/web/
RUN pnpm --filter web build

# --- Stage 2: Django runtime ----------------------------------------------
FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_DEBUG=0

WORKDIR /app

# Python deps via pipenv (system install — no nested virtualenv in the image).
RUN pip install pipenv
COPY backend/Pipfile backend/Pipfile.lock ./
RUN pipenv install --system --deploy

# App code.
COPY backend/ ./

# Built SPA from stage 1 -> where settings.FRONTEND_DIR expects it.
COPY --from=frontend /repo/apps/web/dist ./frontend

# Collect Django's own static (admin / DRF browsable API) into STATIC_ROOT.
RUN python manage.py collectstatic --noinput

# Persist SQLite outside the image layer (see docker-compose volume).
VOLUME ["/app/data"]
ENV DJANGO_DB_PATH=/app/data/db.sqlite3

EXPOSE 8000
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
