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
│   ├── pyproject.toml          # Ruff + pytest configuration
│   ├── project.json            # Nx project definition ("api")
│   ├── manage.py
│   ├── core/                   # Django settings, urls, wsgi (asgi added in Phase 3)
│   └── matches/                # Scoring domain
│       ├── models.py           # Team, Player, Match, Innings, BallEvent
│       ├── serializers.py      # DRF serializers (explicit fields + validation)
│       ├── services.py         # Scoring engine: rules, extras, strike rotation
│       ├── views.py            # API endpoints for scoring & live match
│       ├── urls.py
│       └── tests/              # pytest-django: test_services.py, test_api.py
│
└── apps/
    └── web/                    # Vue 3 + TypeScript + Vite + Tailwind (pnpm/Nx)
        ├── package.json
        ├── project.json        # Nx project ("web"): build, test, typecheck
        ├── vite.config.ts      # Dev server + /api proxy + Vitest config (see NETWORK.md)
        ├── tsconfig.json       # TypeScript config
        ├── tailwind.config.js  # Functional palette tokens (see PALETTE.md)
        ├── postcss.config.js
        └── src/
            ├── main.ts
            ├── App.vue
            ├── types.ts        # Shared domain types (mirror the API)
            ├── api/            # client.ts — typed fetch wrapper (relative /api)
            ├── stores/         # Pinia stores: match.ts (+ .test.ts)
            ├── router/         # Route table (/setup, /match/:id/score, …)
            ├── views/          # Setup, ScorerDashboard, ViewerLive, History (.vue)
            └── components/     # ScoreHeader, WicketModal, ExtrasModal, OpenersModal (+ .test.ts)
```

## Testing

- **Backend:** `pnpm nx run api:test` (pytest-django)
- **Frontend:** `pnpm nx run web:test` (Vitest) · `pnpm nx run web:typecheck` (vue-tsc)

## Root-Level Commands

Run everything from the repo root (see [PHASES.md](PHASES.md) for the full config):

- **Serve backend:** `pnpm nx run api:serve` (or `pnpm api:serve`)
- **Serve frontend:** `pnpm nx run web:serve` (or `pnpm web:serve`)
- **Make migrations:** `pnpm nx run api:mm`
- **Run migrations:** `pnpm nx run api:migrate`
