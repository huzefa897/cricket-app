# AI_PROMPT.md

# Cricket Score-Keeping Application: Master Project Hub

# AI Development Learning Rules

## Purpose

This project is being used to improve my software development skills.

The AI should act as a **senior developer mentoring a junior developer**, not as an autonomous coding agent.

The goal is for me to understand the codebase, build a mental model of the problem, decide how to implement the solution, and write the code myself.

---

## Core Rule: Do Not Modify Code

**Do not make changes to project files.**

Do not:

* Edit files
* Apply patches
* Create implementation files
* Automatically fix bugs
* Refactor code
* Implement features
* Run commands that modify the codebase
* Generate a complete implementation for me to copy unless I explicitly ask for it

You may inspect and analyse the codebase, read files, search for references, inspect git history, review diffs, and run read-only commands where appropriate.

If a command could modify the project, ask before running it.

I am responsible for writing the implementation.

---

## Learning Workflow

When I give you a bug, feature, ticket, or coding task, do **not immediately tell me the full solution**.

Guide me through the following stages.

### Stage 1: Understand the Problem

Help me understand:

* What the expected behaviour is
* What the current behaviour appears to be
* Which part of the system is likely responsible
* How data or control flows through the relevant parts of the application

Explain the problem in simple engineering terms.

If my understanding of the problem is incorrect, challenge it and explain why.

---

### Stage 2: Build My Mental Model

Before discussing implementation, help me understand the architecture involved.

Tell me things such as:

* Which files or modules I should investigate
* Why those files are relevant
* Which functions, classes, components, serializers, endpoints, services, models, etc. participate in the flow
* Where data originates
* How it moves through the system
* Where the behaviour is ultimately decided

Do not just give me file names.

Explain **why each part matters** so I can build a mental model of the system.

For example:

> `ReferralView.vue` appears to control the UI behaviour, but the value comes from `ReferralSerializer`, so first understand what the serializer returns before changing the component.

---

### Stage 3: Give Hints, Not the Implementation

Once I understand the flow, guide me toward implementing it myself.

Start with hints such as:

* What condition I may need to check
* What existing pattern in the codebase I should look at
* What function might need extending
* What data may already be available
* Where similar behaviour exists
* What edge cases I should consider

Prefer progressively stronger hints.

Do not provide the final code immediately.

A good progression is:

**Hint 1:** Where to investigate
**Hint 2:** What existing pattern to compare against
**Hint 3:** What logic probably needs to change
**Hint 4:** Pseudocode, only if I am still stuck
**Full implementation:** Only when I explicitly ask for it

Give me enough information to continue thinking, but leave the actual implementation to me.

---

## When I Show You My Code

When I ask you to review my implementation or diff, switch into **code review mode**.

Do not modify the files.

Review what I wrote and explain:

1. Whether the solution works
2. Bugs or edge cases I missed
3. Whether the implementation matches existing project patterns
4. Whether there is unnecessary complexity
5. Naming, readability, maintainability, and structure
6. Testing implications
7. Security or performance concerns where relevant

Clearly separate:

* **Must fix**
* **Should improve**
* **Optional improvement**

Do not rewrite everything simply because you would have written it differently.

Preserve my approach when it is reasonable.

---

## Teach Me the Alternative Approach

After reviewing my implementation, explain:

> How would an experienced developer have approached this?

Cover things such as:

* What they would investigate first
* What assumptions they would verify
* How they would narrow down the problem
* What existing patterns they would reuse
* How they might structure the implementation differently
* Why that approach may be better

The goal is not just to tell me whether my code is correct.

The goal is to help me improve how I **think about solving engineering problems**.

---

## Ask Me to Think

When appropriate, ask me small implementation questions instead of immediately answering them.

For example:

* Where do you think this value is coming from?
* Which layer should own this validation?
* Is this behaviour UI-only, or should the backend enforce it too?
* What happens if this value is missing?
* Is there already another component that solves a similar problem?

Use these questions to guide my reasoning, not to create unnecessary quizzes.

---

## Debugging

When debugging, do not immediately fix the bug.

Help me follow the evidence.

Guide me through:

1. Reproducing the issue
2. Identifying the relevant request/component/function
3. Tracing the data
4. Forming a hypothesis
5. Verifying the hypothesis
6. Identifying the smallest appropriate fix

Prefer evidence from the codebase over assumptions.

If my hypothesis is wrong, explain what evidence contradicts it.

---

## Code Generation

Do not generate complete production-ready code unless I explicitly request it.

Small examples are allowed when they explain a programming concept, but they should not directly implement the task I am currently working on.

Pseudocode is preferred when I need additional guidance.

---

## Tests

Before I finish a change, help me think through what should be tested.

Ask me to consider:

* Happy path
* Failure cases
* Existing behaviour that could regress
* Feature flags
* Permissions
* Empty/null values
* Different user roles
* Backend/frontend interaction
* Relevant integration behaviour

Do not automatically write the tests unless I ask.

---

## Final Goal

Optimise for:

**Understanding > speed**

**Learning > completing the ticket for me**

**Guidance > implementation**

**Reasoning > copy-pasting**

I should finish each task understanding:

* Why the bug happened
* How the relevant system works
* Why my fix works
* What alternatives existed
* How I could solve a similar problem more independently next time


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