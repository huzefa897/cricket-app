"""API views — thin controllers that validate input and delegate to services."""

from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import services
from .models import Match
from .serializers import (
    BallInputSerializer,
    MatchCreateSerializer,
    MatchDetailSerializer,
    MatchListSerializer,
    OpenersSerializer,
)


def _active_innings(match: Match):
    """The most recent, not-yet-completed innings (what scoring acts on)."""
    return match.innings.filter(is_completed=False).order_by("-innings_number").first()


@api_view(["GET", "POST"])
def matches(request):
    """GET: history list. POST: create a match + open Innings 1."""
    if request.method == "GET":
        qs = Match.objects.all()
        return Response(MatchListSerializer(qs, many=True).data)

    serializer = MatchCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    match = services.create_match(**serializer.validated_data)
    return Response(MatchDetailSerializer(match).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def match_detail(request, match_id):
    """Full match detail (rosters + innings) — used for the history scorecard."""
    match = get_object_or_404(Match, pk=match_id)
    return Response(MatchDetailSerializer(match).data)


@api_view(["GET"])
def match_live(request, match_id):
    """Real-time state for scorer + viewer (polled every few seconds)."""
    match = get_object_or_404(Match, pk=match_id)
    return Response(services.build_live_state(match))


@api_view(["POST"])
def set_openers(request, match_id):
    """Set striker / non-striker / bowler for the active innings."""
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


@api_view(["POST"])
def record_ball(request, match_id):
    """Record one delivery on the active innings."""
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


@api_view(["POST"])
def transition_innings(request, match_id):
    """End Innings 1 and open Innings 2 (swap sides, set new openers)."""
    match = get_object_or_404(Match, pk=match_id)
    serializer = OpenersSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        services.transition_innings(match, **serializer.validated_data)
    except DjangoValidationError as exc:
        return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
    return Response(services.build_live_state(match))


@api_view(["POST"])
def finish_match(request, match_id):
    """Manually finish the match and lock scoring."""
    match = get_object_or_404(Match, pk=match_id)
    try:
        services.finish_match(match)
    except DjangoValidationError as exc:
        return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
    return Response(services.build_live_state(match))
