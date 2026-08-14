# Visual System and Color Direction

## 1. Product Design Direction

Howzatt is an operational scoring tool used on phones at the boundary, not a
marketing surface. The interface should feel energetic where a scorer is making
ball-by-ball decisions and quieter where someone is setting up or reviewing a
match.

- **Recognition before decoration:** color identifies scoring actions, live
  state, selection, completion, and errors.
- **Scorer-first hierarchy:** score, active players, and the next valid action
  must remain the strongest signals.
- **Calm utility screens:** Home, Setup, History, and Viewer use shared controls
  and lower-intensity surfaces so buttons and statuses remain easy to scan.
- **Mobile and outdoor use:** text, borders, placeholders, selected states, and
  disabled states must remain legible on a phone in uneven light.
- **Consistent behavior across themes:** changing theme changes presentation,
  not component meaning or workflow.

## 2. Theme Architecture

The selected theme is stored in `localStorage` by
`apps/web/src/stores/preferences.ts`. `App.vue` applies it to
`<html data-theme="...">`. Dedicated scorer dashboard classes provide the more
intense console treatment, while utility views use the shared control classes
defined in `style.css`.

Each entry in `apps/web/src/designs/registry.ts` combines:

1. An app-wide CSS skin in `apps/web/src/style.css`.
2. A scorer dashboard component implementing the shared contract in
   `apps/web/src/designs/contract.ts`.

The shipped themes are:

- **Frosted (default):** dark violet base, orange/magenta light fields, frosted
  read panels, violet primary actions, amber extras, and coral wicket/live
  states. The scorer uses dedicated `.glass` and `.btn-*` treatments; utility
  routes use the shared button/list/toggle vocabulary.
- **Classic Light:** off-white canvas, white cards, and the original functional
  cricket palette. It remains the quieter bright alternative; a dedicated
  sunlight/high-contrast mode is still Phase 2 work.

Adding a theme requires a registry entry, a dashboard implementing the shared
contract, and scoped CSS overrides. Views must not branch on a theme ID.

## 3. Functional Color Vocabulary

The original Tailwind tokens remain the semantic source of truth for Classic
Light and the fallback styles:

| Role          | Token      | Classic value | Meaning                                    |
| ------------- | ---------- | ------------- | ------------------------------------------ |
| Canvas        | `canvas`   | `#F8F9FA`     | App background                             |
| Card          | `card`     | `#FFFFFF`     | Read surfaces and modal panels             |
| Standard runs | `runs`     | `#475569`     | Dot balls and runs 1-3                     |
| Boundaries    | `boundary` | `#9333EA`     | Fours, sixes, and boundary emphasis        |
| Wides         | `wide`     | `#D97706`     | Wide extras                                |
| No-balls      | `noball`   | `#0D9488`     | No-ball extras                             |
| Byes          | `bye`      | `#64748B`     | Byes and leg-byes                          |
| Wickets       | `wicket`   | `#A34838`     | Dismissals and destructive match actions   |
| System        | `system`   | `#4A6B5D`     | Navigation, selection, and primary actions |

Frosted remaps these roles without changing their meaning:

- **World:** `#3A1D8A` to `#150E30`, with `#FF7A45` and `#B23CFF`
  light fields.
- **Primary/boundary:** `#8B5CF6` to `#7C3AED`.
- **Extras:** `#E0952F` to `#C97E1E`.
- **Wicket:** `#E0503F` to `#C23A2B`.
- **Live:** coral `#FF6B6B` with an explicit `LIVE` label and dot.
- **Completed:** emerald-tinted badge; **upcoming:** neutral glass badge.

Live, completed, and upcoming states must use both text and color. Live color is
not reused for an unrelated action.

## 4. Shared Utility Controls

Home, Setup, and History use shared classes from `style.css` instead of
assembling theme-specific Tailwind strings in every view:

- `.btn-primary` and `.btn-secondary`
- `.toggle` and `.chip`, with `.on` for selection
- `.list-card` and `.chev`
- `.badge-done`, `.badge-upcoming`, and `.live-badge`
- `.hint` for validation guidance

Every control needs a readable default, selected, disabled, active, and focus
state in both themes. Frosted form placeholders and borders intentionally use
stronger opacity than decorative glass so they remain usable.

## 5. Motion and Feedback

- Route changes use a short cross-fade.
- Modal panels fade and rise to communicate state changes.
- List updates use a short movement transition.
- Live indicators pulse; scoring buttons compress on active press.
- `Toast.vue` provides error, success, info, and warning feedback above modals.
- `prefers-reduced-motion: reduce` collapses animation durations app-wide.

Motion must communicate navigation, state, or feedback. It must not delay
scoring or hide content while an animation initializes.
