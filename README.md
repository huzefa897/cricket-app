# 🏏 Howzatt — Local-First Cricket Scoring App

A mobile-optimized, local-first cricket scoring web app for weekend matches. Runs
entirely on a laptop at the ground (acting as a Wi-Fi hotspot) so scorers and
spectators can use it from their phones without mobile data.

**Stack:** Django + Django REST Framework · Vue 3 (Vite) · SQLite · Docker

## Planning & Design Docs

All specifications live in [`docs/`](docs/) and are treated as **living documentation** —
they must be updated in the same commit as any feature or architectural change.

| Doc | Purpose |
| --- | --- |
| [OVERVIEW.md](docs/OVERVIEW.md) | Index + MVP feature matrix and local-vs-cloud strategy |
| [AI_PROMPT.md](docs/AI_PROMPT.md) | Master hub: tech stack, principles, canonical component pattern |
| [SCOPE.md](docs/SCOPE.md) | MVP boundaries, scoring rules, edge cases, API map |
| [SCHEMA.md](docs/SCHEMA.md) | Database models and how scoring rules flow through them |
| [REPO.md](docs/REPO.md) | Repository directory layout |
| [PHASES.md](docs/PHASES.md) | Monorepo (Nx + pnpm) config and the phased roadmap |
| [UI_PLAN.md](docs/UI_PLAN.md) | Screen-by-screen UX and the Wicket Wizard flow |
| [PALETTE.md](docs/PALETTE.md) | Functional color-coding system |
| [NETWORK.md](docs/NETWORK.md) | Local network & field deployment (`cricket.local`) |

## Getting Started

Requires [asdf](https://asdf-vm.com/) with the `python` and `nodejs` plugins.

```bash
# 1. Toolchain (from repo root; reads .tool-versions)
asdf install                       # python 3.11.9 + nodejs 20.20.2
corepack enable                    # provides pnpm 8.15.9

# 2. Frontend + Nx workspace deps
pnpm install

# 3. Backend deps (Pipenv virtualenv)
cd backend && pipenv install --dev && cd ..

# 4. Initialize the database
pnpm nx run api:migrate

# 5. Run it (two terminals)
pnpm api:serve                     # Django on 0.0.0.0:8000
pnpm web:serve                     # Vite on 0.0.0.0:5173 (proxies /api → Django)
```

## Status

✅ **Pre-phase 1 complete** — Nx + pnpm monorepo scaffold, Pipenv-managed Django
backend (boots, migrates, DRF registered), and a runnable Vue 3 + Vite + Tailwind
frontend skeleton. Both projects (`api`, `web`) are wired into Nx.

⏭️ **Next: Phase 1 (Local Docker MVP)** — the `matches` app (5 models from
[SCHEMA.md](docs/SCHEMA.md)), the scoring engine, the 4 API endpoints, and the 4
frontend views. See [PHASES.md](docs/PHASES.md).
