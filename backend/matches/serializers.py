"""DRF serializers — explicit fields + input validation before the engine runs."""

from rest_framework import serializers

from .models import (
    BallEvent,
    ExtraType,
    Innings,
    Match,
    Player,
    Team,
    TossDecision,
    WicketType,
)


# --------------------------------------------------------------------------- #
# Input serializers
# --------------------------------------------------------------------------- #
class PlayerInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    is_wicket_keeper = serializers.BooleanField(default=False)
    is_captain = serializers.BooleanField(default=False)


class MatchCreateSerializer(serializers.Serializer):
    team_one_name = serializers.CharField(max_length=100)
    team_two_name = serializers.CharField(max_length=100)
    team_one_short = serializers.CharField(max_length=10, allow_blank=True, default="")
    team_two_short = serializers.CharField(max_length=10, allow_blank=True, default="")
    team_one_players = PlayerInputSerializer(many=True)
    team_two_players = PlayerInputSerializer(many=True)
    total_overs = serializers.IntegerField(min_value=1, max_value=100)
    toss_winner_index = serializers.ChoiceField(choices=[1, 2])
    toss_decision = serializers.ChoiceField(choices=TossDecision.values)

    def validate(self, data):
        if len(data["team_one_players"]) < 2 or len(data["team_two_players"]) < 2:
            raise serializers.ValidationError("Each team needs at least 2 players.")
        return data


class OpenersSerializer(serializers.Serializer):
    striker_id = serializers.IntegerField()
    non_striker_id = serializers.IntegerField()
    bowler_id = serializers.IntegerField()


class BowlerChangeSerializer(serializers.Serializer):
    bowler_id = serializers.IntegerField()


class BallInputSerializer(serializers.Serializer):
    runs_scored_bat = serializers.IntegerField(min_value=0, max_value=6, default=0)
    extra_type = serializers.ChoiceField(choices=ExtraType.values, default=ExtraType.NONE)
    extra_runs = serializers.IntegerField(min_value=0, default=0)
    is_wicket = serializers.BooleanField(default=False)
    wicket_type = serializers.ChoiceField(choices=WicketType.values, default=WicketType.NONE)
    player_dismissed_id = serializers.IntegerField(required=False, allow_null=True)
    incoming_batsman_id = serializers.IntegerField(required=False, allow_null=True)
    new_striker_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        if data["is_wicket"] and data["wicket_type"] == WicketType.NONE:
            raise serializers.ValidationError("wicket_type is required when is_wicket is true.")
        if data["extra_type"] in (ExtraType.WIDE, ExtraType.NO_BALL) and data["extra_runs"] < 1:
            raise serializers.ValidationError(
                "Wides and no-balls must include at least the 1-run penalty in extra_runs."
            )
        return data


# --------------------------------------------------------------------------- #
# Output serializers (history & scorecard)
# --------------------------------------------------------------------------- #
class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["id", "name", "is_wicket_keeper", "is_captain"]


class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ["id", "name", "short_code", "players"]


class InningsSerializer(serializers.ModelSerializer):
    batting_team = serializers.CharField(source="batting_team.name", read_only=True)
    bowling_team = serializers.CharField(source="bowling_team.name", read_only=True)
    overs = serializers.CharField(source="overs_display", read_only=True)
    crr = serializers.FloatField(source="run_rate", read_only=True)

    class Meta:
        model = Innings
        fields = [
            "id",
            "innings_number",
            "batting_team",
            "bowling_team",
            "total_runs",
            "total_wickets",
            "overs",
            "crr",
            "is_completed",
        ]


class MatchListSerializer(serializers.ModelSerializer):
    team_one = serializers.CharField(source="team_one.name", read_only=True)
    team_two = serializers.CharField(source="team_two.name", read_only=True)

    class Meta:
        model = Match
        fields = [
            "id",
            "team_one",
            "team_two",
            "total_overs",
            "status",
            "created_at",
        ]


class MatchDetailSerializer(serializers.ModelSerializer):
    team_one = TeamSerializer(read_only=True)
    team_two = TeamSerializer(read_only=True)
    toss_winner = serializers.CharField(source="toss_winner.name", read_only=True, default=None)
    innings = InningsSerializer(many=True, read_only=True)

    class Meta:
        model = Match
        fields = [
            "id",
            "team_one",
            "team_two",
            "total_overs",
            "toss_winner",
            "toss_decision",
            "status",
            "created_at",
            "innings",
        ]


class BallEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = BallEvent
        fields = [
            "id",
            "over_number",
            "ball_number_in_over",
            "runs_scored_bat",
            "extra_type",
            "extra_runs",
            "is_wicket",
            "wicket_type",
        ]
