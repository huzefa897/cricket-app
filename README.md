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

## Status

📋 Planning complete. Implementation not yet started — see [PHASES.md](docs/PHASES.md)
for the Phase 1 (Local Docker MVP) breakdown.
