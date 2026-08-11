# SCOPE

# Cricket Score-Keeping Application: Project Blueprint & Scope

## 1. Project Overview & Architecture Strategy

- **Target Audience:** Local weekend cricket matches.
- **Primary Interface:** Responsive Web App (optimized for smartphone usage on the field, with laptop/desktop support for setup and history).
- **Local-First Deployment Strategy:**
    - Runs inside a single **Docker container** on a local laptop.
    - The laptop acts as a Wi-Fi hotspot on the cricket ground.
    - The scorer accesses the app locally via a smartphone browser (bypassing poor mobile internet coverage).
    - Spectators can also connect to the local network to view live scores.
- **Tech Stack:**
    - **Backend:** Python Django (Django REST Framework)
    - **Frontend:** Vue.js
    - **Database:** SQLite (File-based, highly portable for local use, easily upgradable to PostgreSQL for cloud deployment later).

---

## 2. Phase 1 Scope (MVP)

### Match Setup & Teams

- **Ad-Hoc Teams (Option A):** No permanent team directories required. When creating a match, the user simply inputs Team Name 1, Team Name 2, and adds player rosters on the fly.
- **Match Configuration:** Total overs configuration, toss winner, and toss decision (Bat/Bowl).

### Roles & Access Control

- **Admin / Scorer:** Has write access via a touch-friendly mobile interface to log deliveries.
- **Viewer:** Read-only access for teammates and spectators to watch live updates in real-time.

### Scoring Engine & Core Rules

- **Legal Deliveries:** Maximum 6 legal balls per over. Over automatically rolls over after 6 legal deliveries.
- **Extras Handling:**
    - **Wides (`WIDE`):** Counts as an extra ball + 1 penalty run (plus any additional runs scampered). Does *not* advance the legal ball count of the over.
    - **No-Balls (`NO_BALL`):** Counts as an extra ball + 1 penalty run (plus runs scored off bat/extras). Does *not* advance the legal ball count.
    - **Byes / Leg-Byes:** Tracked accordingly.
- **Strike Rotation:**
    - Automatic strike rotation on odd runs scored off the bat (1, 3).
    - Automatic strike rotation at the end of every completed over.
- **End-of-Over Bowler Change:** When an over completes (6 legal balls) and the innings
  is still live, the scorer is prompted to select the next bowler before any further
  delivery can be logged. The same bowler cannot bowl two overs in a row.
- **Boundaries:** Tracks individual 4s and 6s for enhanced scorecards.

### Match Completion & History

- **Innings Transitions:** Auto-calculates the target (1st innings score + 1), swaps batting and bowling teams, and prompts for new opening batsmen/bowlers.
- **Post-Match & Local History:** Saves completed matches to local SQLite storage to review past game scorecards and stats.

---

## 3. Edge Cases & Rule Handling Strategy

### 1. Complex Extras (Wides & No-Balls)

- **Wides (`WIDE`):** Logged as an extra ball. Automatically adds the mandatory penalty run (plus any extra runs scampered). **Rule:** Does *not* increment the legal ball count of the over (the over extends until 6 legal deliveries are bowled).
- **No-Balls (`NO_BALL`):** Logged as an extra ball. Automatically adds the mandatory penalty run (plus runs scored off the bat or extras). **Rule:** Does *not* increment the legal ball count of the over.

### 2. Run Outs & Manual Strike Deciders

- **Dismissal Workflow:** When a wicket falls, a pop-up appears allowing the scorer to select the wicket type (Bowled, Caught, Run Out, Stumped, LBW) and identify the dismissed player.
- **Strike Management on Run Outs:** To prevent logic bugs from complex mid-pitch crossing, the app provides a **manual strike decider** prompt, allowing the scorer to explicitly select who remains on strike and who the incoming batsman is.

### 3. Innings Transitions

- **Automatic Target Calculation:** When the 1st innings concludes (all wickets down or overs completed), the system automatically calculates the target score (`1st_innings_runs + 1`).
- **Team & Role Swapping:** Automatically swaps the batting and bowling teams for the 2nd innings.
- **Initialization Prompt:** Immediately prompts the scorer to input the new opening batsmen and opening bowler before the first ball of the 2nd innings can be logged.

---

## 4. Future Roadmap

- **Phase 2: Polish & Field Testing**
    - Robust "Undo last ball" and error correction features.
    - High-contrast UI mode for bright outdoor sunlight.
    - Export scorecards as images for WhatsApp groups.
- **Phase 3: Cloud Migration & Global Viewing**
    - Migrate SQLite to PostgreSQL.
    - Deploy Django backend to a cloud host (Render/Fly.io) and Vue frontend to a static CDN (Vercel/Netlify).
    - Real-time WebSockets for remote viewers anywhere in the world.
- **Phase 4: Tournaments & Leagues**
    - Multi-team tournament scheduling (Round-robin, Knockouts).
    - Automated points table and Net Run Rate (NRR) calculations.
    - Season-long player career statistics.
- **Phase 5: Advanced Ecosystem**
    - Offline-first Progressive Web App (PWA) caching.
    - Worm charts and momentum graphs.

---

## 5. Database Schema (Django ORM Models)

### Team

- `id`: Auto-incrementing Primary Key
- `name`: String (e.g., "Saturday XI")
- `short_code`: String (e.g., "SAT")

### Player

- `id`: Auto-incrementing Primary Key
- `team`: Foreign Key $\rightarrow$ Team
- `name`: String
- `is_wicket_keeper`: Boolean
- `is_captain`: Boolean

### Match

- `id`: Auto-incrementing Primary Key
- `team_one`: Foreign Key $\rightarrow$ Team
- `team_two`: Foreign Key $\rightarrow$ Team
- `total_overs`: Integer
- `toss_winner`: Foreign Key $\rightarrow$ Team (Nullable)
- `toss_decision`: String (`BAT` or `BOWL`)
- `status`: String (`UPCOMING`, `LIVE`, `COMPLETED`)
- `created_at`: DateTime

### Innings

- `id`: Auto-incrementing Primary Key
- `match`: Foreign Key $\rightarrow$ Match
- `batting_team`: Foreign Key $\rightarrow$ Team
- `bowling_team`: Foreign Key $\rightarrow$ Team
- `innings_number`: Integer (`1` or `2`)
- `total_runs`: Integer (Default: 0)
- `total_wickets`: Integer (Default: 0)
- `legal_balls_bowled`: Integer (Tracks legal deliveries for over calculations)
- `current_striker`: Foreign Key $\rightarrow$ Player (Nullable)
- `current_non_striker`: Foreign Key $\rightarrow$ Player (Nullable)
- `current_bowler`: Foreign Key $\rightarrow$ Player (Nullable)
- `is_completed`: Boolean (Default: False)

### BallEvent (Delivery)

- `id`: Auto-incrementing Primary Key
- `innings`: Foreign Key $\rightarrow$ Innings
- `over_number`: Integer
- `ball_number_in_over`: Integer (1 to 6; only increments on legal deliveries)
- `batsman`: Foreign Key $\rightarrow$ Player
- `bowler`: Foreign Key $\rightarrow$ Player
- `runs_scored_bat`: Integer (0, 1, 2, 3, 4, 6)
- `extra_type`: String (`NONE`, `WIDE`, `NO_BALL`, `BYE`, `LEG_BYE`)
- `extra_runs`: Integer
- `is_wicket`: Boolean
- `wicket_type`: String (`NONE`, `BOWLED`, `CAUGHT`, `RUN_OUT`, `STUMPED`, `LBW`)
- `player_dismissed`: Foreign Key $\rightarrow$ Player (Nullable)

---

## 6. Core API Endpoints Map (DRF)

- **`POST /api/matches/`**
    - *Purpose:* Initialize a match with ad-hoc team names, rosters, and overs. Sets up Innings 1.
- **`GET /api/matches/{id}/live/`**
    - *Purpose:* Fetch real-time match state JSON (score, CRR, RRR, current batters/bowlers) for Scorer and Viewer interfaces.
- **`POST /api/matches/{id}/balls/`**
    - *Purpose:* Submit a delivery payload. Triggers backend rule validations (over increments, extra calculations, strike rotation, and wicket processing).
- **`POST /api/matches/{id}/bowler/`**
    - *Purpose:* Change the current bowler at the end of an over. Payload `{ bowler_id }`.
      Rejects a batting-team player, the same bowler two overs running, and a completed innings.
- **`POST /api/matches/{id}/innings/transition/`**
    - *Purpose:* Concludes Innings 1, computes target, swaps teams, and initializes Innings 2 opening constraints.