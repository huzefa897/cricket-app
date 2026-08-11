from django.urls import path

from . import views

urlpatterns = [
    path("matches/", views.MatchesView.as_view(), name="matches"),
    path("matches/<int:match_id>/", views.MatchDetailView.as_view(), name="match-detail"),
    path("matches/<int:match_id>/live/", views.MatchLiveView.as_view(), name="match-live"),
    path("matches/<int:match_id>/openers/", views.SetOpenersView.as_view(), name="match-openers"),
    path("matches/<int:match_id>/balls/", views.RecordBallView.as_view(), name="match-balls"),
    path(
        "matches/<int:match_id>/innings/transition/",
        views.TransitionInningsView.as_view(),
        name="match-transition",
    ),
    path("matches/<int:match_id>/finish/", views.FinishMatchView.as_view(), name="match-finish"),
]
