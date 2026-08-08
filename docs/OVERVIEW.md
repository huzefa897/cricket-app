# Project Overview

- [AI_PROMPT.md](AI_PROMPT.md) — Master project hub, tech stack, engineering principles, canonical component pattern.
- [SCOPE.md](SCOPE.md) — Engineering principles, MVP boundaries, edge cases, schema, API map.
- [REPO.md](REPO.md) — Repository directory layout.
- [PHASES.md](PHASES.md) — Monorepo config and the phased roadmap.
- [SCHEMA.md](SCHEMA.md) — Database models and how scoring rules flow through them.
- [UI_PLAN.md](UI_PLAN.md) — Screen-by-screen UX and the Wicket Wizard flow.
- [PALETTE.md](PALETTE.md) — Functional color-coding system.
- [NETWORK.md](NETWORK.md) — Local network & field deployment.

| **Component** | **Local MVP (Docker on Laptop)** | **Cloud Production Scale** | **How Hard is the Switch?** |
| --- | --- | --- | --- |
| **Database** | SQLite (File-based) | PostgreSQL (Managed Cloud SQL) | **Very Easy** (Handled entirely by Django config) |
| **Backend** | Docker container on your laptop | Cloud container service (Render, Fly.io, AWS ECS, Google Cloud Run) | **Very Easy** (You deploy the exact same Dockerfile) |
| **Frontend** | Served directly by Django | Cached on a CDN (Vercel / Netlify) or served via Django | **Easy** (Vue builds into static files) |

| **Feature Category** | **Included in MVP Scope** |
| --- | --- |
| **Platform & Users** | Smartphone app with role-based access: **Admin/Scorer** (write access) and **Viewer** (read-only access). |
| **Match Setup** | Team creation, player rosters, match overs configuration, and toss. |
| **Scoring Rules Engine** | Automated enforcement (max 6 legal balls per over, automatic strike rotation on odd runs/end of over). |
| **Live Interface & Dashboards** | Fast ball-by-ball inputs, current score, CRR/RRR, batter/bowler running stats. |
| **Match Completion & History** | Full post-match scorecard summary and a local history list to view past games. |