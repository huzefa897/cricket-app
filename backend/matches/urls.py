from django.urls import path

from . import views

urlpatterns = [
    path("matches/", views.matches, name="matches"),
    path("matches/<int:match_id>/", views.match_detail, name="match-detail"),
    path("matches/<int:match_id>/live/", views.match_live, name="match-live"),
    path("matches/<int:match_id>/openers/", views.set_openers, name="match-openers"),
    path("matches/<int:match_id>/balls/", views.record_ball, name="match-balls"),
    path(
        "matches/<int:match_id>/innings/transition/",
        views.transition_innings,
        name="match-transition",
    ),
]
