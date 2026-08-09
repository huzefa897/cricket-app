# AI_PROMPT.md

# Cricket Score-Keeping Application: Master Project Hub

## 1. What is this App?

A local-first, mobile-optimized cricket scoring web application designed specifically for weekend matches. It runs entirely inside a local Docker container or natively via Nx on a local laptop at the cricket ground, acting as a Wi-Fi hotspot so scorers and spectators can access it seamlessly via smartphone browsers without relying on mobile internet data.

## 2. Modular Documentation Index

To keep development clean, maintainable, and aligned with YAGNI and SOLID principles, all detailed project specifications are split into dedicated living markdown files.

> **Important Rule:** These files are **living documentation**. Whenever a feature is completed or an architectural change is made, these files **must** be updated immediately in the same commit.
> 
- [**REPO.md**](REPO.md) — Repository structure, `asdf` tool versions (`.tool-versions`), `Nx` monorepo configuration, `pnpm` workspaces, and native execution commands (`pnpm nx run api:serve`, `pnpm nx run web:serve`).
- [**SCHEMA.md**](SCHEMA.md) — Complete database schema (`Team`, `Player`, `Match`, `Innings`, `BallEvent`), relational constraints, and core Django model specifications.
- [**UI_PLAN.md**](UI_PLAN.md) — Screen-by-screen UX workflows (`/setup`, `/match/{id}/score`, `/match/{id}/live`, `/history`) and the 5-step Wicket Wizard modal flow.
- [**PALETTE.md**](PALETTE.md) — The mandatory functional color-coding system (Off-white canvas, white cards, slate runs, purple boundaries, ochre wides, teal no-balls, rust wickets, and sage system actions).
- [**SCOPE.md**](SCOPE.md) — Engineering principles (SOLID, YAGNI), architectural guardrails, and Phase 1 MVP boundaries.
- [**PHASES.md**](PHASES.md) — Detailed milestone breakdown, implementation tracking, and phased roadmap toward full MVP delivery.

## 3. Quick-Start Developer Workflow

### Environment Tooling (`asdf`)

Ensure your local environment matches the workspace version requirements specified in `.tool-versions`:

- Python (`3.11.x`)
- Node.js (`20.x`)
- pnpm (`8.x`)

### Root-Level Execution Commands (Nx + Pipenv)

You can run both frontend and backend services directly from the project root without needing to build Docker containers for local debugging:

- **Start Backend API:** `pnpm nx run api:serve` (or `pnpm api:serve`)
- **Start Frontend Web App:** `pnpm nx run web:serve` (or `pnpm web:serve`)
- **Make Database Migrations:** `pnpm nx run api:mm` (or `pnpm api:mm`)
- **Run Database Migrations:** `pnpm nx run api:migrate`
- **Fake Migrations:** `pnpm nx run api:migrate-fake`

## 4. Code Quality & Standards

- **Python Backend:** Managed via Pipenv. Linting and auto-formatting handled by **Ruff** (configured via `pyproject.toml` and `.pre-commit-config.yaml` with auto-fix enabled).
- **Vue 3 Frontend:** Built using Composition API (`<script setup>`) and follows the strict canonical component styling and functional color tokens defined in `PALETTE.md`.

## 2. Repo Structure & Tech Stack

### Tech Stack

- **Monorepo:** Nx + pnpm workspaces (single root, run everything from the top).
- **Backend:** Python Django (Django REST Framework), managed via **Pipenv**.
- **Frontend:** Vue.js 3 + **TypeScript** (`<script setup lang="ts">` / Vite), state via
  **Pinia**, styled with **Tailwind CSS**.
- **Testing:** **Vitest** + `@vue/test-utils` (frontend) and **pytest** + **pytest-django**
  (backend). Every feature ships with tests — run `pnpm nx run web:test` and
  `pnpm nx run api:test`.
- **Database:** SQLite (File-based, persistent local storage; Postgres deferred to Phase 3).
- **Containerization:** Docker & Docker Compose.
- **Live updates (Phase 1):** HTTP polling of `GET /live` (WebSockets deferred to Phase 3 — see [NETWORK.md](NETWORK.md)).

> **Testing policy:** every new feature must ship with both backend and frontend tests
> (or whichever layer it touches). Behavior is locked in by tests before we move on.

### Repository Directory Layout

See [REPO.md](REPO.md) for the full annotated tree. In brief:

```
howzatt/
├── backend/                  # Django Backend (DRF, Pipenv)
│   ├── core/                 # settings, urls, wsgi
│   ├── matches/              # models, serializers, services (scoring engine), views, urls
│   ├── Pipfile               # Python dependencies & script aliases
│   ├── project.json          # Nx project ("api")
│   └── manage.py
├── apps/
│   └── web/                  # Vue 3 + Vite + Tailwind (Nx project "web")
│       ├── src/              # views/, components/, composables/, router/, App.vue
│       ├── project.json
│       └── vite.config.js
├── Dockerfile                # Multi-stage build (Node build of apps/web + Python runtime)
├── docker-compose.yml        # Local orchestration & volume persistence
├── nx.json / pnpm-workspace.yaml / package.json
└── docs/                     # Living documentation (this folder)
```

## 3. Engineering Principles & Guidelines

### SOLID Principles

- **S (Single Responsibility):** Each Django model/view and Vue component must have only one reason to change (e.g., separating scoring logic from UI rendering).
- **O (Open/Closed):** Software entities should be open for extension but closed for modification (e.g., modular extra types in the scoring engine).
- **L (Liskov Substitution):** Subclasses must be substitutable for their base classes without altering correct behavior.
- **I (Interface Segregation):** API endpoints and frontend components should only expose data and props relevant to their direct consumers.
- **D (Dependency Inversion):** Depend upon abstractions, not concretions (use clean service layers and composables for API communication).

### YAGNI (You Aren't Gonna Need It)

- **Do not add code, models, or UI features unless explicitly required by the current scope.**
- Stick strictly to Phases MVP features
- No premature optimization or speculative features.

## 4. How to Work in This Repo

1. **Local Environment:** Spin up the stack using `docker-compose up --build`.
2. **Branching & Commits:** Keep commits small, descriptive, and atomic.
3. **Design System Compliance:** All UI components must adhere strictly to the functional color scheme:
    - Canvas: Off-White (`#F8F9FA`) | Cards: Pure White (`#FFFFFF`)
    - Standard Runs: Soft Slate Gray (`#475569`)
    - Boundaries: Rich Royal Purple (`#9333EA`)
    - Wides: Warm Ochre (`#D97706`)
    - No-Balls: Teal (`#0D9488`)
    - Byes/Leg-Byes: Muted Slate Blue (`#64748B`)
    - Wickets: Terracotta Rust (`#A34838`)
    - System Actions: Deep Sage Green (`#4A6B5D`)

## 5. Backend (`/backend` - Django) Instructions

- **Keep Views Lean:** Use Django REST Framework (DRF) ModelSerializers and viewsets/APIViews. Push core business rules (such as over-extension calculations and target updates) into model methods or clean service classes.
- **Database Integrity:** Ensure all ball events validate against active innings constraints. Never allow a ball event to commit if the innings is marked completed.
- **Serializers:** Explicitly declare fields and validate input payloads before hitting database transactions.

## 6. Frontend (`/frontend` - Vue 3) Instructions

- **Composition API:** Always use Vue 3 `<script setup>` with Composition API (`ref`, `computed`, etc.).
- **State Management:** Keep local component state local; share global live match data using lightweight composables or reactive stores.
- **Mobile Responsiveness:** Prioritize touch-target sizing (minimum 48px height/width) for outdoor thumb usage.

## 7. How to Write a Frontend Component (Canonical Pattern)

Every Vue 3 component must follow this canonical structural pattern to maintain consistency across the codebase:

Code snippet

```
<script setup>
import { ref, computed } from 'vue'

// 1. Define Props & Emits
const props = defineProps({
  label: {
    type: String,
    required: true
  },
  variant: {
    type: String,
    default: 'runs'
  }
})

const emit = defineEmits(['click'])

// 2. Reactive State & Computed Properties
const isPressed = ref(false)

// Variants map to the semantic Tailwind tokens defined in PALETTE.md
const buttonClass = computed(() => {
  const variants = {
    runs: 'bg-runs text-white',          // dots & singles
    boundary: 'bg-boundary text-white',  // 4s & 6s
    wicket: 'bg-wicket text-white',      // dismissals
    system: 'bg-system text-white',      // primary actions
    wide: 'bg-wide text-white',          // wides
    noball: 'bg-noball text-white',      // no-balls
    bye: 'bg-bye text-white'             // byes / leg-byes
  }
  return variants[props.variant] || variants.runs
})

// 3. Methods & Handlers
const handleClick = (event) => {
  emit('click', event)
}
</script>

<template>
  <button
    class="px-4 py-3 rounded-lg font-semibold shadow-sm transition-transform active:scale-95 focus:outline-none focus:ring-2 focus:ring-offset-2"
    :class="buttonClass"
    @click="handleClick"
  >
    {{ label }}
  </button>
</template>

<style scoped>
/* Optional scoped tweaks if utility classes need local support */
</style>
```