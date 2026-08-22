"""API views — thin controllers that validate input and delegate to services."""

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import Innings, Match
from .serializers import (
    BallInputSerializer,
    BowlerChangeSerializer,
    MatchCreateSerializer,
    MatchDetailSerializer,
    MatchListSerializer,
    OpenersSerializer,
)


def _active_innings(match: Match):
    """The most recent, not-yet-completed innings (what scoring acts on)."""
    return match.innings.filter(is_completed=False).order_by("-innings_number").first()


class MatchesView(APIView):
    """GET: history list. POST: create a match + open Innings 1."""

    def get(self, request):
        # Prefetch innings (+ batting team) so live_summary adds no per-row queries.
        qs = Match.objects.select_related("team_one", "team_two").prefetch_related(
            Prefetch("innings", queryset=Innings.objects.select_related("batting_team"))
        )
        return Response(MatchListSerializer(qs, many=True).data)

    def post(self, request):
        serializer = MatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        match = services.create_match(**serializer.validated_data)
        return Response(MatchDetailSerializer(match).data, status=status.HTTP_201_CREATED)


class MatchDetailView(APIView):
    """Full match detail (rosters + innings) — used for the history scorecard."""

    def get(self, request, match_id):
        match = get_object_or_404(Match, pk=match_id)
        return Response(MatchDetailSerializer(match).data)


class MatchLiveView(APIView):
    """Real-time state for scorer + viewer (polled every few seconds)."""

    def get(self, request, match_id):
        match = get_object_or_404(Match, pk=match_id)
        return Response(services.build_live_state(match))


class SetOpenersView(APIView):
    """Set striker / non-striker / bowler for the active innings."""

    def post(self, request, match_id):
        match = get_object_or_404(Match, pk=match_id)
        innings = _active_innings(match)
        if innings is None:
            return Response({"detail": "No active innings."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = OpenersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            services.set_openers(innings, **serializer.validated_data)
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(services.build_live_state(match))


class ChangeBowlerView(APIView):
    """Change the bowler at the end of an over."""

    def post(self, request, match_id):
        match = get_object_or_404(Match, pk=match_id)
        innings = _active_innings(match)
        if innings is None:
            return Response({"detail": "No active innings."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = BowlerChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            services.change_bowler(innings, **serializer.validated_data)
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(services.build_live_state(match))


class RecordBallView(APIView):
    """Record one delivery on the active innings."""

    def post(self, request, match_id):
        match = get_object_or_404(Match, pk=match_id)
        innings = _active_innings(match)
        if innings is None:
            return Response(
                {"detail": "No active innings to score."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = BallInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            services.record_ball(innings, **serializer.validated_data)
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(services.build_live_state(match))


class UndoBallEventView(APIView):
    """Undo feature which helps reversing a ball event"""

    def post(self, request, match_id):
        match = get_object_or_404(Match, pk=match_id)
        innings = _active_innings(match)
        if innings is None:
            return Response(
                {"detail": "No active innings to score."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            services.undo_last_ball(innings)
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(services.build_live_state(match))


class TransitionInningsView(APIView):
    """End Innings 1 and open Innings 2 (swap sides, set new openers)."""

    def post(self, request, match_id):
        match = get_object_or_404(Match, pk=match_id)
        serializer = OpenersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            services.transition_innings(match, **serializer.validated_data)
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(services.build_live_state(match))


class FinishMatchView(APIView):
    """Manually finish the match and lock scoring."""

    def post(self, request, match_id):
        match = get_object_or_404(Match, pk=match_id)
        try:
            services.finish_match(match)
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(services.build_live_state(match))
