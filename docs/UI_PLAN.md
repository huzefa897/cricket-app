# Cricket Score-Keeping Application: UI/UX Master Plan & Design Architecture

## 1. General Design Principles & Environment

- **Primary Context:** Outdoor use under bright sunlight (requires high-contrast themes and bold, legible fonts).
- **Device Priority:** Mobile-first layout optimized for thumb-reach on smartphones (since scorers are actively tapping inputs from the boundary or dugout).
- **Frictionless Navigation:** Minimal menus, zero clunky pop-ups outside of critical error workflows, and large touch targets to prevent accidental mis-taps.
- **Functional Color:** Strong color communicates scoring action, selection, status,
  or feedback. Utility pages remain visually quieter than the scoring console.
- **Theme Consistency:** Frosted and Classic Light preserve the same workflows and
  meanings. Theme selection is presentation-only and persists on the device.
- **Accessible Motion:** Transitions communicate route or modal state and respect
  `prefers-reduced-motion`.

---

## 2. Screen-by-Screen Breakdown & User Flow

### A. Home Screen (`/`)

- **Purpose:** Entry point for starting, resuming, or reviewing a match.
- **Current Behavior:**
    - Polls the match list every 5 seconds and shows active matches under **Live now**.
    - Live cards show teams, current batting summary, overs, and a shared `LIVE` badge.
    - Tapping a live card resumes the scorer route.
    - Primary and secondary actions open Match Setup and Match History.

### B. Match Setup Screen (`/setup`)

- **Target User:** Scorer / Admin preparing the game before the first ball.
- **Current Behavior:**
    - Accepts ad-hoc team names, optional short codes, and on-the-fly player names.
    - Displays removable player chips and a live player count for each team.
    - Provides preset/custom overs, toss-winner toggles, and Bat/Bowl decision toggles.
    - Requires both team names and at least two players per side. The disabled
      primary action includes a short validation hint explaining what is missing.
    - **Start Match & Open Scorer** creates the match and routes to scoring.

### C. Scorer Dashboard (`/match/{id}/score`)

- **Target User:** The active scorer tapping inputs rapidly under pressure.
- **Current Behavior:**
    - Renders the dashboard component associated with the selected theme.
    - Shows score/wickets, overs, CRR/RRR/target, active batters, bowler figures,
      and the current-over ticker.
    - Keeps the thumb-friendly grid for dot/1/2/3, 4/6, extras, and wicket.
    - Frosted uses a single-column phone layout and a two-column console on larger screens.
    - Prompts for openers, innings transition, and a new bowler when required.
    - Supports manual match finish with confirmation and routes completed matches to the scorecard view.
    - Exposes theme settings from the scorer screen and persists the choice locally.
    - Displays API/action failures through the reusable toast above modal layers.

### D. Viewer Live Dashboard (`/match/{id}/live`)

- **Target User:** Teammates, substitutes, or remote spectators viewing from their own devices.
- **Current Behavior:**
    - Polls every 3 seconds and renders a larger read-only score summary.
    - Shows a horizontal current-over ticker and current batter/bowler figures.
    - Shows a completed-match banner when scoring is locked.

### E. Local Match History (`/history`)

- **Target User:** Anyone reviewing past weekend fixtures.
- **Current Behavior:**
    - Lists locally stored matches with teams, overs, creation time, and status.
    - Uses a shared live badge plus distinct completed/upcoming badges.
    - Tapping a live/upcoming match opens scoring; tapping a completed match opens
      the read-only live/scorecard route.

---

## 3. The Wicket Wizard Flow (Step-by-Step Modal)

To completely eliminate scorer errors during high-stress dismissal events, tapping **"Wicket!"** opens a sequential, guided modal wizard equipped with back buttons at every stage.

- **Step 1: Dismissal Type**
    - *UI:* A large touch-button grid.
    - *Options:* `Bowled` | `Caught` | `Run Out` | `Stumped` | `LBW`
    - *Control:* Tapping any button instantly progresses to Step 2.
- **Step 2: Who Got Out?**
    - *Runs completed (run-outs only):* When the dismissal is `Run Out`, a `0 / 1 / 2 / 3`
      selector appears first to capture runs completed before the dismissal. These are
      credited to the striker off the delivery (`runs_scored_bat`); other dismissal types
      always record zero bat runs.
    - *UI:* Two large split-screen buttons.
    - *Options:* `Striker (Current Batsman)` vs `Non-Striker`
    - *Control:* Tapping a choice advances to Step 3.
- **Step 3: Incoming Batsman**
    - *UI:* A searchable dropdown/select list populated exclusively with remaining active players from the batting team's roster.
    - *Control:* Selects the player and clicks `Next`.
- **Step 4: Next Strike Decider**
    - *UI:* Decision buttons to handle complex cross-over rules (vital for run-outs).
    - *Options:* `Incoming batsman takes strike` vs `Non-striker stays on strike`
    - *Control:* Selects one and clicks `Next`.
- **Step 5: Overview & Confirmation (The Safety Net)**
    - *UI:* A clean summary card displaying all configured details:
        - Dismissal Type, Dismissed Player, Incoming Player, and Next Striker position.
    - *Controls:*
        - `[Edit]` buttons next to each row to jump backward and change a specific field.
        - A bottom `[Back]` button to return to the previous step.
        - A prominent **`[Confirm & Send]`** button that securely packages the configuration into the API payload and logs the delivery.

## 4. End-of-Over Bowler Modal

When an over completes (6 legal balls) and the innings is still live, the scorer must
nominate the next bowler before scoring can continue.

- **Trigger:** a `needsBowler` flag on the Scorer dashboard — true when `legal_balls_bowled`
  is a positive multiple of 6, the innings is not complete, and openers are already set.
- **Behavior:** the modal (`BowlerModal`) presents a single dropdown of the bowling side's
  players; `[Confirm]` posts `{ bowler_id }` to `POST /api/matches/{id}/bowler/`.
- **Guardrail:** the scoring matrix is hidden while the prompt is open, so no delivery can be
  logged until a new bowler is chosen. The backend rejects the same bowler two overs in a row.

## 5. Shipped Design System Additions

The post-MVP UI expansion introduced:

- Theme registry and shared scorer dashboard contract.
- Frosted and Classic Light dashboards.
- Device-local theme persistence and a Settings modal.
- Shared `LiveBadge`, utility buttons, toggles, chips, list cards, badges, and hints.
- Route, modal, and list transitions with reduced-motion handling.
- Reusable toast variants for error, success, info, and warning feedback.

See [PALETTE.md](PALETTE.md) for color roles and implementation rules.

## 6. Deferred UI Scope

These items appeared in the original design plan but are not implemented yet:

- Smart team/player autocomplete and permanent directories.
- Undo or edit-last-ball controls.
- Viewer tabs and complete batting/bowling scorecard tables.
- Expanded history summaries with winner, top scorer, and full scorecards.
- Dedicated sunlight/high-contrast mode validated through field testing.
- Scorer passcode or account-based route protection.
