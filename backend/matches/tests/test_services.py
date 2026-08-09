"""Unit tests for the scoring engine (matches/services.py)."""

import pytest
from django.core.exceptions import ValidationError

from matches import services
from matches.models import Innings, MatchStatus


def active_innings(match):
    return match.innings.filter(is_completed=False).order_by("-innings_number").first()


# --------------------------------------------------------------------------- #
# Match setup
# --------------------------------------------------------------------------- #
class TestCreateMatch:
    def test_creates_teams_rosters_and_first_innings(self, make_match):
        match, meta = make_match(players_per_side=3)
        assert match.status == MatchStatus.LIVE
        assert match.team_one.players.count() == 3
        assert match.team_two.players.count() == 3
        inns = match.innings.get(innings_number=1)
        assert inns.batting_team_id == match.team_one_id  # toss winner chose BAT

    def test_toss_winner_bowl_makes_other_team_bat(self, make_match):
        match, _ = make_match(toss_winner_index=1, toss_decision="BOWL")
        inns = match.innings.get(innings_number=1)
        assert inns.batting_team_id == match.team_two_id


# --------------------------------------------------------------------------- #
# Openers
# --------------------------------------------------------------------------- #
class TestSetOpeners:
    def test_rejects_same_striker_and_non_striker(self, make_match):
        match, meta = make_match()
        inns = match.innings.get(innings_number=1)
        with pytest.raises(ValidationError):
            services.set_openers(
                inns,
                striker_id=meta["one"][0],
                non_striker_id=meta["one"][0],
                bowler_id=meta["two"][0],
            )

    def test_rejects_bowler_from_batting_team(self, make_match):
        match, meta = make_match()
        inns = match.innings.get(innings_number=1)
        with pytest.raises(ValidationError):
            services.set_openers(
                inns,
                striker_id=meta["one"][0],
                non_striker_id=meta["one"][1],
                bowler_id=meta["one"][2],  # wrong team
            )


# --------------------------------------------------------------------------- #
# Recording deliveries
# --------------------------------------------------------------------------- #
class TestRecordBall:
    def test_dot_ball_increments_legal_count_only(self, opened_match):
        match, _ = opened_match
        inns = active_innings(match)
        services.record_ball(inns, runs_scored_bat=0)
        inns.refresh_from_db()
        assert inns.total_runs == 0
        assert inns.legal_balls_bowled == 1

    def test_runs_off_bat_added_to_total(self, opened_match):
        match, _ = opened_match
        services.record_ball(active_innings(match), runs_scored_bat=4)
        inns = active_innings(match)
        assert inns.total_runs == 4
        assert inns.legal_balls_bowled == 1

    def test_wide_adds_penalty_but_does_not_advance_over(self, opened_match):
        match, _ = opened_match
        services.record_ball(active_innings(match), extra_type="WIDE", extra_runs=1)
        inns = active_innings(match)
        assert inns.total_runs == 1
        assert inns.legal_balls_bowled == 0  # over not advanced

    def test_no_ball_penalty_plus_bat_runs(self, opened_match):
        match, _ = opened_match
        services.record_ball(
            active_innings(match), extra_type="NO_BALL", extra_runs=1, runs_scored_bat=4
        )
        inns = active_innings(match)
        assert inns.total_runs == 5  # 1 penalty + 4 off bat
        assert inns.legal_balls_bowled == 0

    def test_odd_runs_rotate_strike(self, opened_match):
        match, meta = opened_match
        inns = active_innings(match)
        before = inns.current_striker_id
        services.record_ball(inns, runs_scored_bat=1)
        inns.refresh_from_db()
        assert inns.current_striker_id != before
        assert inns.current_striker_id == meta["one"][1]

    def test_even_runs_keep_strike(self, opened_match):
        match, meta = opened_match
        inns = active_innings(match)
        services.record_ball(inns, runs_scored_bat=2)
        inns.refresh_from_db()
        assert inns.current_striker_id == meta["one"][0]

    def test_over_completion_swaps_strike(self, opened_match):
        match, meta = opened_match
        inns = active_innings(match)
        # 6 dot balls -> over complete -> ends swap (striker unchanged by dots,
        # then over-end swap flips to the non-striker).
        for _ in range(6):
            services.record_ball(active_innings(match), runs_scored_bat=0)
        inns.refresh_from_db()
        assert inns.legal_balls_bowled == 6
        assert inns.current_striker_id == meta["one"][1]

    def test_rejects_ball_when_openers_not_set(self, make_match):
        match, _ = make_match()
        inns = match.innings.get(innings_number=1)
        with pytest.raises(ValidationError):
            services.record_ball(inns, runs_scored_bat=1)


# --------------------------------------------------------------------------- #
# Wickets
# --------------------------------------------------------------------------- #
class TestWickets:
    def test_wicket_replaces_striker_and_tracks_dismissed(self, opened_match):
        match, meta = opened_match
        inns = active_innings(match)
        striker = inns.current_striker_id
        services.record_ball(
            inns,
            is_wicket=True,
            wicket_type="BOWLED",
            player_dismissed_id=striker,
            incoming_batsman_id=meta["one"][2],
            new_striker_id=meta["one"][2],
        )
        inns.refresh_from_db()
        assert inns.total_wickets == 1
        assert inns.current_striker_id == meta["one"][2]
        state = services.build_live_state(match)
        assert striker in state["innings"]["dismissed_player_ids"]

    def test_all_out_completes_innings(self, make_match):
        # 2 players/side => all out at 1 wicket.
        match, meta = make_match(players_per_side=2)
        inns = match.innings.get(innings_number=1)
        services.set_openers(
            inns,
            striker_id=meta["one"][0],
            non_striker_id=meta["one"][1],
            bowler_id=meta["two"][0],
        )
        services.record_ball(
            inns,
            is_wicket=True,
            wicket_type="BOWLED",
            player_dismissed_id=meta["one"][0],
        )
        inns.refresh_from_db()
        assert inns.total_wickets == 1
        assert inns.is_completed is True


# --------------------------------------------------------------------------- #
# Innings completion & transition
# --------------------------------------------------------------------------- #
class TestInningsFlow:
    def test_overs_exhausted_completes_innings(self, opened_match):
        match, _ = opened_match  # 2 overs
        for _ in range(12):
            inns = active_innings(match)
            if inns is None:
                break
            services.record_ball(inns, runs_scored_bat=0)
        first = match.innings.get(innings_number=1)
        assert first.legal_balls_bowled == 12
        assert first.is_completed is True

    def test_transition_swaps_sides_and_sets_target(self, opened_match):
        match, meta = opened_match
        # Score 10 in innings 1, then bowl out the overs.
        services.record_ball(active_innings(match), runs_scored_bat=4)
        services.record_ball(active_innings(match), runs_scored_bat=6)
        for _ in range(12):
            inns = active_innings(match)
            if inns is None:
                break
            services.record_ball(inns, runs_scored_bat=0)

        second = services.transition_innings(
            match,
            striker_id=meta["two"][0],
            non_striker_id=meta["two"][1],
            bowler_id=meta["one"][0],
        )
        assert second.innings_number == 2
        assert second.batting_team_id == match.team_two_id
        state = services.build_live_state(match)
        assert state["innings"]["target"] == 11  # 10 + 1

    def test_chasing_target_completes_match(self, opened_match):
        match, meta = opened_match
        services.record_ball(active_innings(match), runs_scored_bat=4)  # inns1 = 4
        for _ in range(12):
            inns = active_innings(match)
            if inns is None:
                break
            services.record_ball(inns, runs_scored_bat=0)
        services.transition_innings(
            match,
            striker_id=meta["two"][0],
            non_striker_id=meta["two"][1],
            bowler_id=meta["one"][0],
        )
        services.record_ball(active_innings(match), runs_scored_bat=6)  # 6 >= target 5
        match.refresh_from_db()
        assert match.status == MatchStatus.COMPLETED


# --------------------------------------------------------------------------- #
# Finish (manual lock)
# --------------------------------------------------------------------------- #
class TestFinishMatch:
    def test_finish_locks_and_completes(self, opened_match):
        match, _ = opened_match
        services.record_ball(active_innings(match), runs_scored_bat=1)
        services.finish_match(match)
        match.refresh_from_db()
        assert match.status == MatchStatus.COMPLETED
        assert not Innings.objects.filter(match=match, is_completed=False).exists()

    def test_cannot_score_after_finish(self, opened_match):
        match, _ = opened_match
        inns = active_innings(match)
        services.finish_match(match)
        with pytest.raises(ValidationError):
            services.record_ball(inns, runs_scored_bat=1)

    def test_double_finish_rejected(self, opened_match):
        match, _ = opened_match
        services.finish_match(match)
        with pytest.raises(ValidationError):
            services.finish_match(match)


# --------------------------------------------------------------------------- #
# Live state derivations
# --------------------------------------------------------------------------- #
class TestLiveState:
    def test_crr_computed(self, opened_match):
        match, _ = opened_match
        services.record_ball(active_innings(match), runs_scored_bat=6)
        state = services.build_live_state(match)
        # 6 runs off 1 ball => CRR 36.0
        assert state["innings"]["crr"] == pytest.approx(36.0)

    def test_this_over_symbols(self, opened_match):
        match, _ = opened_match
        services.record_ball(active_innings(match), runs_scored_bat=4)
        services.record_ball(active_innings(match), extra_type="WIDE", extra_runs=1)
        state = services.build_live_state(match)
        assert state["innings"]["this_over"] == ["4", "1wd"]
