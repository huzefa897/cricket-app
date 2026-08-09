"""Integration tests for the DRF endpoints (matches/views.py)."""

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()


CREATE_PAYLOAD = {
    "team_one_name": "Strikers",
    "team_two_name": "Blasters",
    "total_overs": 2,
    "team_one_players": [{"name": "A1"}, {"name": "A2"}, {"name": "A3"}],
    "team_two_players": [{"name": "B1"}, {"name": "B2"}, {"name": "B3"}],
    "toss_winner_index": 1,
    "toss_decision": "BAT",
}


def create_match(client, **overrides):
    payload = {**CREATE_PAYLOAD, **overrides}
    res = client.post("/api/matches/", payload, format="json")
    assert res.status_code == 201, res.content
    return res.json()


def set_openers(client, match):
    a = match["team_one"]["players"]
    b = match["team_two"]["players"]
    res = client.post(
        f"/api/matches/{match['id']}/openers/",
        {"striker_id": a[0]["id"], "non_striker_id": a[1]["id"], "bowler_id": b[0]["id"]},
        format="json",
    )
    assert res.status_code == 200, res.content
    return res.json()


@pytest.mark.django_db
class TestMatchApi:
    def test_create_returns_detail_with_rosters(self, client):
        match = create_match(client)
        assert match["status"] == "LIVE"
        assert len(match["team_one"]["players"]) == 3
        assert len(match["innings"]) == 1

    def test_create_validates_min_players(self, client):
        res = client.post(
            "/api/matches/",
            {**CREATE_PAYLOAD, "team_one_players": [{"name": "solo"}]},
            format="json",
        )
        assert res.status_code == 400

    def test_history_lists_matches(self, client):
        create_match(client)
        res = client.get("/api/matches/")
        assert res.status_code == 200
        assert len(res.json()) == 1

    def test_record_ball_updates_live_state(self, client):
        match = create_match(client)
        set_openers(client, match)
        res = client.post(
            f"/api/matches/{match['id']}/balls/", {"runs_scored_bat": 4}, format="json"
        )
        assert res.status_code == 200
        assert res.json()["innings"]["total_runs"] == 4

    def test_ball_before_openers_rejected(self, client):
        match = create_match(client)
        res = client.post(
            f"/api/matches/{match['id']}/balls/", {"runs_scored_bat": 1}, format="json"
        )
        assert res.status_code == 400

    def test_wicket_requires_wicket_type(self, client):
        match = create_match(client)
        set_openers(client, match)
        res = client.post(
            f"/api/matches/{match['id']}/balls/",
            {"is_wicket": True},
            format="json",
        )
        assert res.status_code == 400

    def test_wide_requires_penalty_in_extra_runs(self, client):
        match = create_match(client)
        set_openers(client, match)
        res = client.post(
            f"/api/matches/{match['id']}/balls/",
            {"extra_type": "WIDE", "extra_runs": 0},
            format="json",
        )
        assert res.status_code == 400

    def test_finish_locks_scoring(self, client):
        match = create_match(client)
        set_openers(client, match)
        mid = match["id"]
        client.post(f"/api/matches/{mid}/balls/", {"runs_scored_bat": 2}, format="json")

        res = client.post(f"/api/matches/{mid}/finish/")
        assert res.status_code == 200
        assert res.json()["status"] == "COMPLETED"

        # Further balls are rejected.
        blocked = client.post(f"/api/matches/{mid}/balls/", {"runs_scored_bat": 1}, format="json")
        assert blocked.status_code == 400

    def test_double_finish_rejected(self, client):
        match = create_match(client)
        set_openers(client, match)
        client.post(f"/api/matches/{match['id']}/finish/")
        res = client.post(f"/api/matches/{match['id']}/finish/")
        assert res.status_code == 400

    def test_live_exposes_dismissed_player_ids(self, client):
        match = create_match(client)
        set_openers(client, match)
        a = match["team_one"]["players"]
        client.post(
            f"/api/matches/{match['id']}/balls/",
            {
                "is_wicket": True,
                "wicket_type": "BOWLED",
                "player_dismissed_id": a[0]["id"],
                "incoming_batsman_id": a[2]["id"],
                "new_striker_id": a[2]["id"],
            },
            format="json",
        )
        live = client.get(f"/api/matches/{match['id']}/live/").json()
        assert a[0]["id"] in live["innings"]["dismissed_player_ids"]
