# UI_UX.md

# Cricket Score-Keeping Application: UI/UX Master Plan & Design Architecture

## 1. General Design Principles & Environment

- **Primary Context:** Outdoor use under bright sunlight (requires high-contrast themes and bold, legible fonts).
- **Device Priority:** Mobile-first layout optimized for thumb-reach on smartphones (since scorers are actively tapping inputs from the boundary or dugout).
- **Frictionless Navigation:** Minimal menus, zero clunky pop-ups outside of critical error workflows, and large touch targets to prevent accidental mis-taps.

---

## 2. Screen-by-Screen Breakdown & User Flow

### A. Match Setup Screen (`/setup`)

- **Target User:** Scorer / Admin preparing the game before the first ball.
- **Layout & Components:**
    - **Team Identification:** Text fields for Team 1 and Team 2 featuring smart autocomplete that queries past SQLite records.
    - **Dynamic Roster Builder:**
        - A search-and-add bar (`"Add player to squad..."`). Typing pulls matches from database records, while a secondary `"Add New"` action instantly saves brand-new players on the fly.
        - A live badge/checklist showing current squad counts (e.g., 11/11 players added) with quick remove ("X") buttons.
    - **Match Configuration Panel:**
        - Overs selector (quick-select pills or numerical input).
        - Toss winner toggles (Team 1 vs Team 2) and toss decision buttons (`Bat` or `Bowl`).
    - **Primary Action:** A full-width, high-visibility **"Start Match & Open Scorer"** button that initializes the database and routes the user.

### B. Scorer Dashboard (`/match/{id}/score`)

- **Target User:** The active scorer tapping inputs rapidly under pressure.
- **Layout & Components:**
    - **Live Match Header (Sticky Top):** Compact summary showing current score/wickets (`124/3`), overs bowled (`14.2`), Run Rate (CRR/RRR), and target.
    - **Active Players Panel:** Two clean rows indicating Striker runs/balls, Non-Striker runs/balls, and the current Bowler's figures.
    - **The Scoring Matrix (Thumb-Friendly Grid):**
        - *Row 1:* `0 (Dot)` | `1` | `2` | `3`
        - *Row 2:* `4 (Boundary)` | `6 (Boundary)`
        - *Row 3:* `Wide` | `No Ball` | `Bye / Leg Bye`
        - *Row 4:* Full-width prominent `Wicket!` button (triggers the Wicket Wizard modal).
    - **Bottom Control Bar:** An **"Undo Last Ball"** safety button and a quick link to inspect the full scorecard.

### C. Viewer Live Dashboard (`/match/{id}/live`)

- **Target User:** Teammates, substitutes, or remote spectators viewing from their own devices.
- **Layout & Components:**
    - **Read-Only Clean Display:** Scaled-up graphics for score and run rate so it can be glanced at from a distance.
    - **Over Ticker History:** A horizontal scrolling ticker mapping the current over deliveries (e.g., `[1] [4] [W] [0] [2] [nb]`).
    - **Tabbed Navigation:** Quick toggle between the live scoreboard view and full batting/bowling statistics tables.

### D. Local Match History (`/history`)

- **Target User:** Anyone reviewing past weekend fixtures.
- **Layout & Components:**
    - Chronological list of completed matches stored locally in SQLite.
    - Tapping a match card expands or opens a detailed post-match summary displaying the winning margin, top run-scorer, and full match scorecards.

---

## 3. The Wicket Wizard Flow (Step-by-Step Modal)

To completely eliminate scorer errors during high-stress dismissal events, tapping **"Wicket!"** opens a sequential, guided modal wizard equipped with back buttons at every stage.

- **Step 1: Dismissal Type**
    - *UI:* A large touch-button grid.
    - *Options:* `Bowled` | `Caught` | `Run Out` | `Stumped` | `LBW`
    - *Control:* Tapping any button instantly progresses to Step 2.
- **Step 2: Who Got Out?**
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