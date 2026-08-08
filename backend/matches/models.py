"""Domain models for cricket scoring.

Mirrors docs/SCHEMA.md. Business rules (over rollover, extras, strike rotation,
wicket handling) live in services.py, not here — models stay thin (SRP).
"""

from django.db import models


class TossDecision(models.TextChoices):
    BAT = "BAT", "Bat"
    BOWL = "BOWL", "Bowl"


class MatchStatus(models.TextChoices):
    UPCOMING = "UPCOMING", "Upcoming"
    LIVE = "LIVE", "Live"
    COMPLETED = "COMPLETED", "Completed"


class ExtraType(models.TextChoices):
    NONE = "NONE", "None"
    WIDE = "WIDE", "Wide"
    NO_BALL = "NO_BALL", "No Ball"
    BYE = "BYE", "Bye"
    LEG_BYE = "LEG_BYE", "Leg Bye"


class WicketType(models.TextChoices):
    NONE = "NONE", "None"
    BOWLED = "BOWLED", "Bowled"
    CAUGHT = "CAUGHT", "Caught"
    RUN_OUT = "RUN_OUT", "Run Out"
    STUMPED = "STUMPED", "Stumped"
    LBW = "LBW", "LBW"


class Team(models.Model):
    name = models.CharField(max_length=100)
    short_code = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    name = models.CharField(max_length=100)
    is_wicket_keeper = models.BooleanField(default=False)
    is_captain = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Match(models.Model):
    team_one = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+")
    team_two = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+")
    total_overs = models.PositiveIntegerField()
    toss_winner = models.ForeignKey(
        Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    toss_decision = models.CharField(max_length=4, choices=TossDecision.choices)
    status = models.CharField(
        max_length=10, choices=MatchStatus.choices, default=MatchStatus.UPCOMING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.team_one} vs {self.team_two}"


class Innings(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="innings")
    batting_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+")
    bowling_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+")
    innings_number = models.PositiveSmallIntegerField()  # 1 or 2

    total_runs = models.PositiveIntegerField(default=0)
    total_wickets = models.PositiveIntegerField(default=0)
    # Counts only legal deliveries (excludes wides / no-balls) — drives over math.
    legal_balls_bowled = models.PositiveIntegerField(default=0)

    current_striker = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    current_non_striker = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    current_bowler = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["innings_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["match", "innings_number"], name="unique_innings_per_match"
            )
        ]

    def __str__(self):
        return f"{self.match} — Innings {self.innings_number}"

    # --- Derived helpers (read-only; no side effects) ---
    @property
    def overs_display(self) -> str:
        """Legal balls as cricket overs, e.g. 14 balls -> '2.2'."""
        return f"{self.legal_balls_bowled // 6}.{self.legal_balls_bowled % 6}"

    @property
    def run_rate(self) -> float:
        if self.legal_balls_bowled == 0:
            return 0.0
        return round(self.total_runs / (self.legal_balls_bowled / 6), 2)


class BallEvent(models.Model):
    """An append-only record of a single delivery."""

    innings = models.ForeignKey(Innings, on_delete=models.CASCADE, related_name="balls")
    over_number = models.PositiveIntegerField()
    # 1..6 for legal deliveries; for wides/no-balls it holds the current legal
    # position in the over (it does not advance the over).
    ball_number_in_over = models.PositiveIntegerField()

    batsman = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="+")
    bowler = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="+")

    runs_scored_bat = models.PositiveIntegerField(default=0)
    extra_type = models.CharField(max_length=10, choices=ExtraType.choices, default=ExtraType.NONE)
    # Runs conceded via extras, INCLUDING the mandatory 1-run penalty for
    # wides/no-balls plus any runs physically scampered.
    extra_runs = models.PositiveIntegerField(default=0)

    is_wicket = models.BooleanField(default=False)
    wicket_type = models.CharField(
        max_length=10, choices=WicketType.choices, default=WicketType.NONE
    )
    player_dismissed = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.innings} — {self.over_number}.{self.ball_number_in_over}"

    @property
    def total_runs(self) -> int:
        return self.runs_scored_bat + self.extra_runs
