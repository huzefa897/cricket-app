# PHASES.md

# Pre-phase 1

## 1. Root Workspace Architecture (`Nx` + `pnpm`)

The repository is structured as an **Nx Monorepo** using **pnpm workspaces**, allowing you to execute both backend and frontend commands directly from the **root** of the project.

python 3.11.9
nodejs 20.20.2
pnpm 8.15.9

### Root Directory Structure

Plaintext

```
howzatt/
├── .tool-versions            # asdf versions (python, node, pnpm)
├── .pre-commit-config.yaml   # Pre-commit hooks with Ruff auto-fix
├── pnpm-workspace.yaml       # pnpm workspace definition
├── nx.json                   # Nx workspace orchestrator config
├── package.json              # Root package scripts & workspace definitions
├── backend/                  # Django Backend (Managed via Pipenv)
│   ├── Pipfile
│   ├── Pipfile.lock
│   ├── pyproject.toml        # Ruff configuration
│   ├── project.json          # Nx project definition for backend
│   └── manage.py
└── apps/
    └── web/                  # Vue 3 + Vite Frontend (Managed via pnpm/Nx)
        ├── package.json
        ├── project.json
        └── src/
```

## 2. Root Workspace Configuration Files

### `pnpm-workspace.yaml`

YAML

```
packages:
  - 'backend'
  - 'apps/*'
```

### `nx.json`

JSON

```
{
  "$schema": "./node_modules/nx/schemas/nx-schema.json",
  "namedInputs": {
    "default": ["{projectRoot}/**/*", "sharedGlobals"],
    "production": ["default"]
  },
  "targetDefaults": {
    "serve": {
      "cache": false
    }
  }
}
```

### Root `package.json`

JSON

```
{
  "name": "howzatt-monorepo",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "api:serve": "nx run api:serve",
    "web:serve": "nx run web:serve",
    "api:migrate": "nx run api:migrate",
    "api:mm": "nx run api:mm"
  },
  "devDependencies": {
    "nx": "18.0.0",
    "prettier": "^3.0.0"
  }
}
```

## 3. Backend Nx Integration (`backend/project.json`)

By placing a `project.json` inside the `backend/` directory, Nx recognizes it as a project (`api`), letting you run it from the root.

JSON

```
{
  "name": "api",
  "projectType": "application",
  "targets": {
    "serve": {
      "executor": "nx:run-commands",
      "options": {
        "command": "pipenv run start",
        "cwd": "backend"
      }
    },
    "migrate": {
      "executor": "nx:run-commands",
      "options": {
        "command": "pipenv run migrate",
        "cwd": "backend"
      }
    },
    "mm": {
      "executor": "nx:run-commands",
      "options": {
        "command": "pipenv run mm",
        "cwd": "backend"
      }
    },
    "migrate-fake": {
      "executor": "nx:run-commands",
      "options": {
        "command": "pipenv run migrate --fake",
        "cwd": "backend"
      }
    }
  }
}
```

## 4. Backend Pipfile Setup (`backend/Pipfile`)

Ini, TOML

```
[packages]
django = "~=4.2"
djangorestframework = "~=3.14"
# NOTE: Phase 1 uses SQLite (bundled with Python) — no DB driver needed.
# psycopg2-binary is added in Phase 3 for the Postgres migration only.

[dev-packages]
ruff = "*"

[scripts]
start = "python manage.py runserver 0.0.0.0:8000"
mm = "python manage.py makemigrations"
migrate = "python manage.py migrate"
```

> Binds to `0.0.0.0` so phones on the field Wi-Fi can reach the dev server — see [NETWORK.md](NETWORK.md).

## 5. Auto-Fixing Pre-commit Configuration (`.pre-commit-config.yaml`)

Configured to automatically format and fix code issues upon staging/committing without rigidly failing your workflow where safe auto-corrections apply.

YAML

```
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      # Run the linter with auto-fix enabled
      - id: ruff
        args: [--fix]
      # Run the formatter
      - id: ruff-format
```

## 6. Daily Root-Level Command Reference

- **Start Backend Server:** `pnpm nx run api:serve` (or `pnpm api:serve`)
- **Start Frontend Server:** `pnpm nx run web:serve` (or `pnpm web:serve`)
- **Make Migrations:** `pnpm nx run api:mm` (or `pnpm api:mm`)
- **Run Migrations:** `pnpm nx run api:migrate`
- **Run Fake Migrations:** `pnpm nx run api:migrate-fake`

### Phase 1: Local Docker MVP (The Ground Zero)

*Focus: Getting the core scoring engine working smoothly offline via your laptop hotspot.*

- **Infrastructure:** Single Docker container on your laptop running Django + SQLite, serving the Vue frontend. Connected via laptop/phone hotspot.
- **Match Setup:** Create teams, add player rosters, configure match overs, and handle the toss.
- **Scoring Engine:** Automated rule enforcement (max 6 legal balls per over, automatic strike rotation on odd runs and end of overs).
- **Role-Based Access:**
    - **Admin/Scorer:** Mobile-friendly interface to log ball-by-ball actions.
    - **Viewer:** Read-only view for teammates/spectators connected to the local network.
- **Match History:** Save completed games to local SQLite storage to view past match summaries and scorecards.

### Phase 2: Polish & Field Testing (The Real-World Loop)

*Focus: Fixing real-world friction points discovered during actual weekend matches.*

- **Error Correction & Undo:** Add robust "Undo last ball" or "Edit past ball" features (crucial for cricket since scorers make mistakes).
- **UI/UX Optimization:** High-contrast mode for bright sunlight outdoors, larger touch targets for frantic scoring, and keyboard shortcuts if scoring from a laptop.
- **Enhanced Match States:** Support for Super Overs, DLS method (optional/basic), retired hurt/batsman changes, and penalty runs.
- **Export Options:** Ability to export match scorecards as an image (for WhatsApp groups) or a PDF.

### Phase 3: Cloud Migration & Global Viewing (The Public Launch)

*Focus: Moving off the laptop hotspot so anyone anywhere can watch.*

- **Cloud Deployment:**
    - Migrate SQLite to a managed cloud database (e.g., PostgreSQL).
    - Deploy the Django backend container to a cloud host (e.g., Render, Fly.io, or AWS).
    - Deploy the Vue frontend to a static CDN (e.g., Vercel or Netlify).
- **Real-Time Live Streaming:** Implement WebSockets (or polling) so remote spectators see score updates instantly without refreshing the page.
- **User Accounts & Authentication:** Allow users to sign up, log in, and claim "Admin" rights for their specific team or match.

### Phase 4: Tournaments & Leagues (The Expansion)

*Focus: Scaling from single matches to full multi-team series.*

- **Tournament Management:** Create leagues, round-robin fixtures, and knockout brackets.
- **Points Table Automation:** Auto-calculate Matches Played, Won, Lost, Tied, Net Run Rate (NRR), and total points.
- **Player Career Stats:** Aggregate historical data across a whole season to show top run-scorers, highest wicket-takers, and MVP leaderboards.

### Phase 5: Advanced Intelligence & Ecosystem (Future-Proofing)

*Focus: Adding premium features once the community is established.*

- **Offline-First PWA (Progressive Web App):** Even in the cloud era, allow scorers to cache the app locally on their phone browser so it handles brief signal drops on the ground seamlessly.
- **Worm & Run-Rate Graphs:** Visual analytics tracking team momentum over overs.
- **Audio/Voice Scoring (Experimental):** Voice-to-text command parsing for hands-free scoring (e.g., "four runs, extra cover").