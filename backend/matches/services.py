"""Scoring engine — all cricket business rules live here (SRP / lean views).

The public entry points are:
    create_match(...)        -> Match          (sets up Innings 1)
    set_openers(...)         -> Innings         (striker/non-striker/bowler)
    record_ball(...)         -> BallEvent       (applies one delivery)
    transition_innings(...)  -> Innings         (ends inns 1, opens inns 2)
    build_live_state(...)    -> dict            (score, CRR/RRR, batters, bowler)

Rules implemented (see docs/SCOPE.md & docs/SCHEMA.md):
  * Max 6 *legal* balls per over. Wides & no-balls do not advance the over.
  * Extras: WIDE/NO_BALL add a mandatory penalty (already included in extra_runs).
  * Strike rotation on odd runs physically run, and at the end of every over.
  * Wickets use a manual strike decider (no auto-cross) to avoid run-out bugs.
  * Innings ends on overs exhausted, all out, or (2nd innings) target reached.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum

from .models import (
    BallEvent,
    ExtraType,
    Innings,
    Match,
    MatchStatus,
    Player,
    Team,
    WicketType,
)

LEGAL_BALLS_PER_OVER = 6


# --------------------------------------------------------------------------- #
# Match setup
# --------------------------------------------------------------------------- #
@transaction.atomic
def create_match(
    *,
    team_one_name: str,
    team_two_name: str,
    team_one_players: list[dict],
    team_two_players: list[dict],
    total_overs: int,
    toss_winner_index: int,  # 1 or 2
    toss_decision: str,  # "BAT" | "BOWL"
    team_one_short: str = "",
    team_two_short: str = "",
) -> Match:
    """Create teams + rosters + the match, and open Innings 1 from the toss."""
    team_one = Team.objects.create(name=team_one_name, short_code=team_one_short)
    team_two = Team.objects.create(name=team_two_name, short_code=team_two_short)

    _bulk_players(team_one, team_one_players)
    _bulk_players(team_two, team_two_players)

    match = Match.objects.create(
        team_one=team_one,
        team_two=team_two,
        total_overs=total_overs,
        toss_winner=team_one if toss_winner_index == 1 else team_two,
        toss_decision=toss_decision,
        status=MatchStatus.LIVE,
    )

    batting, bowling = _first_innings_sides(match, toss_winner_index, toss_decision)
    Innings.objects.create(
        match=match,
        batting_team=batting,
        bowling_team=bowling,
        innings_number=1,
    )
    return match


def _bulk_players(team: Team, players: list[dict]) -> None:
    Player.objects.bulk_create(
        [
            Player(
                team=team,
                name=p["name"],
                is_wicket_keeper=p.get("is_wicket_keeper", False),
                is_captain=p.get("is_captain", False),
            )
            for p in players
        ]
    )


def _first_innings_sides(
    match: Match, toss_winner_index: int, toss_decision: str
) -> tuple[Team, Team]:
    """Resolve who bats first from the toss winner + their decision."""
    winner = match.team_one if toss_winner_index == 1 else match.team_two
    loser = match.team_two if toss_winner_index == 1 else match.team_one
    if toss_decision == "BAT":
        return winner, loser
    return loser, winner


# --------------------------------------------------------------------------- #
# Openers
# --------------------------------------------------------------------------- #
def set_openers(
    innings: Innings, *, striker_id: int, non_striker_id: int, bowler_id: int
) -> Innings:
    """Set the on-field players for an innings (openers or post-transition)."""
    striker = _player_in_team(striker_id, innings.batting_team_id)
    non_striker = _player_in_team(non_striker_id, innings.batting_team_id)
    bowler = _player_in_team(bowler_id, innings.bowling_team_id)
    if striker_id == non_striker_id:
        raise ValidationError("Striker and non-striker must be different players.")

    innings.current_striker = striker
    innings.current_non_striker = non_striker
    innings.current_bowler = bowler
    innings.save(update_fields=["current_striker", "current_non_striker", "current_bowler"])
    return innings


def _player_in_team(player_id: int, team_id: int) -> Player:
    try:
        player = Player.objects.get(pk=player_id)
    except Player.DoesNotExist as exc:
        raise ValidationError(f"Player {player_id} does not exist.") from exc
    if player.team_id != team_id:
        raise ValidationError(f"Player {player_id} is not in the expected team.")
    return player


# --------------------------------------------------------------------------- #
# Recording a delivery
# --------------------------------------------------------------------------- #
@transaction.atomic
def record_ball(
    innings: Innings,
    *,
    runs_scored_bat: int = 0,
    extra_type: str = ExtraType.NONE,
    extra_runs: int = 0,
    is_wicket: bool = False,
    wicket_type: str = WicketType.NONE,
    player_dismissed_id: int | None = None,
    incoming_batsman_id: int | None = None,
    new_striker_id: int | None = None,
) -> BallEvent:
    """Apply a single delivery: persist it and mutate the innings state."""
    innings = Innings.objects.select_for_update().get(pk=innings.pk)
    _validate_ball(innings, extra_type, runs_scored_bat)

    is_legal = extra_type not in (ExtraType.WIDE, ExtraType.NO_BALL)
    over_number = innings.legal_balls_bowled // LEGAL_BALLS_PER_OVER
    legal_in_over = innings.legal_balls_bowled % LEGAL_BALLS_PER_OVER
    ball_number_in_over = legal_in_over + 1 if is_legal else legal_in_over

    ball = BallEvent.objects.create(
        innings=innings,
        over_number=over_number,
        ball_number_in_over=ball_number_in_over,
        batsman=innings.current_striker,
        bowler=innings.current_bowler,
        runs_scored_bat=runs_scored_bat,
        extra_type=extra_type,
        extra_runs=extra_runs,
        is_wicket=is_wicket,
        wicket_type=wicket_type,
        player_dismissed_id=player_dismissed_id,
    )

    # 1) Score + counters
    innings.total_runs += runs_scored_bat + extra_runs
    if is_legal:
        innings.legal_balls_bowled += 1
    if is_wicket:
        innings.total_wickets += 1

    # 2) Strike changes. Wickets use the manual decider; otherwise auto-rotate
    #    on odd runs physically run between the wickets.
    if is_wicket:
        _apply_wicket_strike(
            innings,
            player_dismissed_id=player_dismissed_id,
            incoming_batsman_id=incoming_batsman_id,
            new_striker_id=new_striker_id,
        )
    elif _runs_physically_run(extra_type, runs_scored_bat, extra_runs) % 2 == 1:
        _swap_strike(innings)

    # 3) End-of-over rotation (only on a legal ball that completes the over)
    over_complete = is_legal and innings.legal_balls_bowled % LEGAL_BALLS_PER_OVER == 0
    if over_complete:
        _swap_strike(innings)

    # 4) Innings / match completion
    _check_innings_completion(innings)

    innings.save()
    return ball


def _validate_ball(innings: Innings, extra_type: str, runs_scored_bat: int) -> None:
    if innings.is_completed:
        raise ValidationError("Cannot record a ball on a completed innings.")
    if innings.current_striker_id is None or innings.current_bowler_id is None:
        raise ValidationError("Set the openers (striker, non-striker, bowler) first.")
    if extra_type in (ExtraType.WIDE, ExtraType.BYE, ExtraType.LEG_BYE) and runs_scored_bat:
        raise ValidationError("runs_scored_bat must be 0 for wides, byes, and leg-byes.")


def _runs_physically_run(extra_type: str, runs_scored_bat: int, extra_runs: int) -> int:
    """How many runs the batters actually ran (what decides crossing).

    The 1-run penalty on a wide/no-ball is not run by the batters, so it is
    excluded when deciding whether they crossed.
    """
    if extra_type == ExtraType.NONE:
        return runs_scored_bat
    if extra_type in (ExtraType.BYE, ExtraType.LEG_BYE):
        return extra_runs
    if extra_type == ExtraType.WIDE:
        return max(extra_runs - 1, 0)  # runs scampered beyond the penalty
    if extra_type == ExtraType.NO_BALL:
        return runs_scored_bat + max(extra_runs - 1, 0)
    return 0


def _swap_strike(innings: Innings) -> None:
    innings.current_striker_id, innings.current_non_striker_id = (
        innings.current_non_striker_id,
        innings.current_striker_id,
    )


def _apply_wicket_strike(
    innings: Innings,
    *,
    player_dismissed_id: int | None,
    incoming_batsman_id: int | None,
    new_striker_id: int | None,
) -> None:
    """Replace the dismissed batter and set strike per the manual decider."""
    if _is_all_out(innings):
        return  # last wicket — no incoming batter needed

    if incoming_batsman_id is None:
        raise ValidationError("An incoming batsman is required for this wicket.")
    incoming = _player_in_team(incoming_batsman_id, innings.batting_team_id)

    # Put the incoming batter into the dismissed player's slot.
    if player_dismissed_id == innings.current_striker_id:
        innings.current_striker = incoming
    elif player_dismissed_id == innings.current_non_striker_id:
        innings.current_non_striker = incoming
    else:
        # Fallback: assume the striker was out.
        innings.current_striker = incoming

    # Manual strike decider (vital for run-outs). Defaults to incoming on strike.
    target_striker_id = new_striker_id or incoming.id
    if target_striker_id == innings.current_non_striker_id:
        _swap_strike(innings)


def _is_all_out(innings: Innings) -> bool:
    roster_size = Player.objects.filter(team_id=innings.batting_team_id).count()
    # All out when wickets == players - 1 (last batter has no partner).
    return innings.total_wickets >= max(roster_size - 1, 1)


def _check_innings_completion(innings: Innings) -> None:
    overs_done = innings.legal_balls_bowled >= innings.match.total_overs * LEGAL_BALLS_PER_OVER
    all_out = _is_all_out(innings)

    chased = False
    if innings.innings_number == 2:
        target = _target_for(innings)
        chased = target is not None and innings.total_runs >= target

    if overs_done or all_out or chased:
        innings.is_completed = True
        if innings.innings_number == 2:
            match = innings.match
            match.status = MatchStatus.COMPLETED
            match.save(update_fields=["status"])


def _target_for(innings: Innings) -> int | None:
    """Runs needed to win in the 2nd innings (1st innings total + 1)."""
    if innings.innings_number != 2:
        return None
    first = innings.match.innings.filter(innings_number=1).first()
    if first is None:
        return None
    return first.total_runs + 1


# --------------------------------------------------------------------------- #
# Innings transition
# --------------------------------------------------------------------------- #
@transaction.atomic
def transition_innings(
    match: Match, *, striker_id: int, non_striker_id: int, bowler_id: int
) -> Innings:
    """Close Innings 1 and open Innings 2 with swapped sides + new openers."""
    first = match.innings.filter(innings_number=1).first()
    if first is None:
        raise ValidationError("No first innings to transition from.")
    if match.innings.filter(innings_number=2).exists():
        raise ValidationError("Second innings already exists.")

    first.is_completed = True
    first.save(update_fields=["is_completed"])

    second = Innings.objects.create(
        match=match,
        batting_team=first.bowling_team,  # sides swap
        bowling_team=first.batting_team,
        innings_number=2,
    )
    return set_openers(
        second,
        striker_id=striker_id,
        non_striker_id=non_striker_id,
        bowler_id=bowler_id,
    )


# --------------------------------------------------------------------------- #
# Live state (for scorer + viewer)
# --------------------------------------------------------------------------- #
def build_live_state(match: Match) -> dict:
    """Assemble the real-time match snapshot consumed by both dashboards."""
    innings = match.innings.order_by("-innings_number").first()
    if innings is None:
        return {"match_id": match.id, "status": match.status, "innings": None}

    target = _target_for(innings)
    balls_remaining = match.total_overs * LEGAL_BALLS_PER_OVER - innings.legal_balls_bowled
    rrr = None
    if target is not None and balls_remaining > 0:
        runs_needed = max(target - innings.total_runs, 0)
        rrr = round(runs_needed / (balls_remaining / 6), 2)

    return {
        "match_id": match.id,
        "status": match.status,
        "total_overs": match.total_overs,
        "innings": {
            "innings_number": innings.innings_number,
            "batting_team": innings.batting_team.name,
            "bowling_team": innings.bowling_team.name,
            "total_runs": innings.total_runs,
            "total_wickets": innings.total_wickets,
            "overs": innings.overs_display,
            "legal_balls_bowled": innings.legal_balls_bowled,
            "is_completed": innings.is_completed,
            "crr": innings.run_rate,
            "rrr": rrr,
            "target": target,
            "striker": _batter_stats(innings, innings.current_striker),
            "non_striker": _batter_stats(innings, innings.current_non_striker),
            "bowler": _bowler_stats(innings, innings.current_bowler),
            "this_over": _this_over(innings),
        },
    }


def _batter_stats(innings: Innings, player: Player | None) -> dict | None:
    if player is None:
        return None
    balls = innings.balls.filter(batsman=player).exclude(extra_type=ExtraType.WIDE)
    runs = balls.aggregate(r=Sum("runs_scored_bat"))["r"] or 0
    return {
        "id": player.id,
        "name": player.name,
        "runs": runs,
        "balls": balls.count(),
    }


def _bowler_stats(innings: Innings, player: Player | None) -> dict | None:
    if player is None:
        return None
    balls = innings.balls.filter(bowler=player)
    legal = balls.exclude(extra_type__in=[ExtraType.WIDE, ExtraType.NO_BALL]).count()
    runs = sum(b.total_runs for b in balls)
    wickets = balls.filter(is_wicket=True).exclude(wicket_type=WicketType.RUN_OUT).count()
    return {
        "id": player.id,
        "name": player.name,
        "overs": f"{legal // 6}.{legal % 6}",
        "runs_conceded": runs,
        "wickets": wickets,
    }


def _this_over(innings: Innings) -> list[str]:
    """Compact symbols for the current over's deliveries (viewer ticker)."""
    current_over = innings.legal_balls_bowled // LEGAL_BALLS_PER_OVER
    symbols = []
    for ball in innings.balls.filter(over_number=current_over):
        symbols.append(_ball_symbol(ball))
    return symbols


def _ball_symbol(ball: BallEvent) -> str:
    if ball.is_wicket:
        return "W"
    if ball.extra_type == ExtraType.WIDE:
        return f"{ball.extra_runs}wd"
    if ball.extra_type == ExtraType.NO_BALL:
        return f"{ball.runs_scored_bat + ball.extra_runs}nb"
    if ball.extra_type in (ExtraType.BYE, ExtraType.LEG_BYE):
        suffix = "b" if ball.extra_type == ExtraType.BYE else "lb"
        return f"{ball.extra_runs}{suffix}"
    return str(ball.runs_scored_bat)
