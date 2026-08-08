# REPO.md

# Repository Structure

Howzatt is an **Nx monorepo** managed with **pnpm workspaces**. The Django backend
is managed with **Pipenv**; the Vue 3 frontend lives under `apps/web/` and is styled
with **Tailwind CSS**. All backend and frontend tasks run from the repo root via Nx.

> Tooling versions are pinned in `.tool-versions` (asdf): Python `3.11.9`,
> Node.js `20.20.2`, pnpm `8.15.9`.

```
howzatt/
├── .tool-versions              # asdf versions (python, node, pnpm)
├── .pre-commit-config.yaml     # Pre-commit hooks with Ruff auto-fix
├── pnpm-workspace.yaml         # pnpm workspace definition (backend, apps/*)
├── nx.json                     # Nx workspace orchestrator config
├── package.json                # Root scripts (api:serve, web:serve, api:migrate…)
├── Dockerfile                  # Multi-stage: build apps/web, run Django + SQLite
├── docker-compose.yml          # Local orchestration & volume persistence
├── docs/                       # Living documentation (this folder)
│
├── backend/                    # Django Backend (DRF, managed via Pipenv)
│   ├── Pipfile                 # Python dependencies & script aliases
│   ├── pyproject.toml          # Ruff configuration
│   ├── project.json            # Nx project definition ("api")
│   ├── manage.py
│   ├── core/                   # Django settings, urls, wsgi (asgi added in Phase 3)
│   └── matches/                # Scoring domain
│       ├── models.py           # Team, Player, Match, Innings, BallEvent
│       ├── serializers.py      # DRF serializers (explicit fields + validation)
│       ├── services.py         # Scoring engine: rules, extras, strike rotation
│       ├── views.py            # API endpoints for scoring & live match
│       └── urls.py
│
└── apps/
    └── web/                    # Vue 3 + Vite + Tailwind (managed via pnpm/Nx)
        ├── package.json
        ├── project.json        # Nx project definition ("web")
        ├── vite.config.js      # Dev server + /api proxy (see NETWORK.md)
        ├── tailwind.config.js  # Functional palette tokens (see PALETTE.md)
        ├── postcss.config.js
        └── src/
            ├── main.js
            ├── App.vue
            ├── router/         # Route table (/setup, /match/:id/score, …)
            ├── views/          # Setup.vue, ScorerDashboard.vue, ViewerLive.vue, History.vue
            ├── components/     # Reusable UI parts (ScoreCard, WicketModal, …)
            └── composables/    # useApi, useLiveMatch (polling), shared state
```

## Root-Level Commands

Run everything from the repo root (see [PHASES.md](PHASES.md) for the full config):

- **Serve backend:** `pnpm nx run api:serve` (or `pnpm api:serve`)
- **Serve frontend:** `pnpm nx run web:serve` (or `pnpm web:serve`)
- **Make migrations:** `pnpm nx run api:mm`
- **Run migrations:** `pnpm nx run api:migrate`
