# Project Overview

- [AI_PROMPT.md](AI_PROMPT.md) — Master project hub, tech stack, engineering principles, canonical component pattern.
- [SCOPE.md](SCOPE.md) — Engineering principles, MVP boundaries, edge cases, schema, API map.
- [REPO.md](REPO.md) — Repository directory layout.
- [PHASES.md](PHASES.md) — Monorepo config and the phased roadmap.
- [SCHEMA.md](SCHEMA.md) — Database models and how scoring rules flow through them.
- [UI_PLAN.md](UI_PLAN.md) — Current screen behavior, design-system additions,
  deferred UI scope, and the Wicket Wizard flow.
- [PALETTE.md](PALETTE.md) — Theme architecture, functional color roles, shared
  utility controls, and motion direction.
- [NETWORK.md](NETWORK.md) — Local network & field deployment.

| **Component** | **Local MVP (Docker on Laptop)** | **Cloud Production Scale** | **How Hard is the Switch?** |
| --- | --- | --- | --- |
| **Database** | SQLite (File-based) | PostgreSQL (Managed Cloud SQL) | **Very Easy** (Handled entirely by Django config) |
| **Backend** | Docker container on your laptop | Cloud container service (Render, Fly.io, AWS ECS, Google Cloud Run) | **Very Easy** (You deploy the exact same Dockerfile) |
| **Frontend** | Served directly by Django | Cached on a CDN (Vercel / Netlify) or served via Django | **Easy** (Vue builds into static files) |

| **Feature Category** | **Included in MVP Scope** |
| --- | --- |
| **Platform & Users** | Smartphone-first scorer and read-only viewer surfaces. Identity-based access control is deferred. |
| **Match Setup** | Team creation, player rosters, match overs configuration, and toss. |
| **Scoring Rules Engine** | Automated enforcement (max 6 legal balls per over, automatic strike rotation on odd runs/end of over). |
| **Live Interface & Dashboards** | Fast ball-by-ball inputs, current score, CRR/RRR, batter/bowler running stats. |
| **Match Completion & History** | Match completion, score locking, and a local history list. Expanded post-match summaries and full scorecard tables are deferred. |
| **Delivered UI Expansion** | Frosted/Classic themes, persisted preference, swappable scorer dashboards, Home live-match polling, shared statuses/controls, toast feedback, and reduced-motion-aware transitions. |

The delivered UI expansion is tracked as **Phase 1.1**. It improves presentation
and navigation but does not pull authentication, undo/edit, smart roster search,
or full scorecard tables into the completed MVP scope.
