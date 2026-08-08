# SCHEMA

# Database

**Core Database Models
1. Team Model**
Represents a cricket team playing in a match.
• **Fields:**
    ◦ `id`: Primary Key (Auto-increment)
    ◦ `name`: String (e.g., "Royal Strikers")
    ◦ `short_code`: String (e.g., "RST" - great for scoreboards)
**2. Player Model**
Represents individual players belonging to a team.
• **Fields:**
    ◦ `id`: Primary Key
    ◦ `team`: Foreign Key $\rightarrow$ Team (Links player to a specific team)
    ◦ `name`: String (e.g., "Virat Kohli")
    ◦ `is_wicket_keeper`: Boolean (Optional helper for UI)
    ◦ `is_captain`: Boolean (Optional helper for UI)
**3. Match Model**
Configures the overall match parameters, teams, and current state.
• **Fields:**
    ◦ `id`: Primary Key
    ◦ `team_one`: Foreign Key $\rightarrow$ Team
    ◦ `team_two`: Foreign Key $\rightarrow$ Team
    ◦ `total_overs`: Integer (e.g., 20 for T20, 10 for custom)
    ◦ `toss_winner`: Foreign Key $\rightarrow$ Team (Null initially)
    ◦ `toss_decision`: String choices (`BAT` or `BOWL`)
    ◦ `status`: String choices (`UPCOMING`, `LIVE`, `COMPLETED`)
    ◦ `created_at`: DateTime
**4. Innings Model**
Tracks the state of a specific innings (A limited-overs match has 2 innings).
• **Fields:**
    ◦ `id`: Primary Key
    ◦ `match`: Foreign Key $\rightarrow$ Match
    ◦ `batting_team`: Foreign Key $\rightarrow$ Team
    ◦ `bowling_team`: Foreign Key $\rightarrow$ Team
    ◦ `innings_number`: Integer (`1` or `2`)
    ◦ `total_runs`: Integer (Default: 0)
    ◦ `total_wickets`: Integer (Default: 0)
    ◦ `legal_balls_bowled`: Integer (Tracks total legal deliveries to calculate overs, e.g., 14 legal balls = 2.2 overs)
    ◦ `current_striker`: Foreign Key $\rightarrow$ Player (Nullable)
    ◦ `current_non_striker`: Foreign Key $\rightarrow$ Player (Nullable)
    ◦ `current_bowler`: Foreign Key $\rightarrow$ Player (Nullable)
    ◦ `is_completed`: Boolean (Default: False)
**5. Revised BallEvent Fields:**
• `id`: Primary Key
• `innings`: Foreign Key $\rightarrow$ Innings
• `over_number`: Integer (Tracks the over)
• `ball_number_in_over`: Integer (**Only increments on legal deliveries**: 1 to 6. Stays the same for Wides/No-Balls).
• `batsman`: Foreign Key $\rightarrow$ Player
• `bowler`: Foreign Key $\rightarrow$ Player
• `runs_scored_bat`: Integer (Runs scored off the bat: 0, 1, 2, 3, 4, 6)
• `extra_type`: Choices (`NONE`, `WIDE`, `NO_BALL`, `BYE`, `LEG_BYE`)
• `extra_runs`: Integer (Runs conceded via extras, e.g., 1 for the wide/no-ball + any extra runs scampered)
• `is_wicket`: Boolean
• `wicket_type`: Choices (`NONE`, `BOWLED`, `CAUGHT`, `RUN_OUT`, `STUMPED`, `LBW`)
• `player_dismissed`: Foreign Key $\rightarrow$ Player (Nullable)
**How the Scoring Rules Flow with this Schema**
1. **Enforcing the "Max 6 Legal Balls" Rule:**
When a ball is logged, your Django backend checks if `extra_type` is a Wide or No-Ball. If it is, it counts as an *illegal* delivery (so the `ball_number_in_over` does not advance, keeping it at the same legal count). If it's a standard ball, `legal_balls_bowled` increments. Once `ball_number_in_over` reaches 6, the system automatically triggers an over-change and swaps the striker/non-striker.
2. **Automatic Strike Rotation:**
If `runs_scored_bat` is odd (1 or 3), your backend automatically swaps `current_striker` and `current_non_striker` in the `Innings` model before saving.