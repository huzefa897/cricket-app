"""Shared pytest fixtures for the matches test suite."""

import pytest

from matches import services


@pytest.fixture
def make_match(db):
    """Factory: create a live match with rosters and return (match, meta).

    meta = {"one": [player_ids...], "two": [player_ids...]} for convenience.
    Defaults: 2 overs, 4 players/side, team one wins toss and bats.
    """

    def _make(
        *,
        total_overs=2,
        players_per_side=4,
        toss_winner_index=1,
        toss_decision="BAT",
    ):
        one = [{"name": f"A{i}"} for i in range(players_per_side)]
        two = [{"name": f"B{i}"} for i in range(players_per_side)]
        match = services.create_match(
            team_one_name="Alpha",
            team_two_name="Bravo",
            team_one_players=one,
            team_two_players=two,
            total_overs=total_overs,
            toss_winner_index=toss_winner_index,
            toss_decision=toss_decision,
        )
        meta = {
            "one": list(match.team_one.players.values_list("id", flat=True)),
            "two": list(match.team_two.players.values_list("id", flat=True)),
        }
        return match, meta

    return _make


@pytest.fixture
def opened_match(make_match):
    """A match with Innings 1 openers set (striker=one[0], non=one[1], bowler=two[0])."""
    match, meta = make_match()
    innings = match.innings.get(innings_number=1)
    services.set_openers(
        innings,
        striker_id=meta["one"][0],
        non_striker_id=meta["one"][1],
        bowler_id=meta["two"][0],
    )
    return match, meta
