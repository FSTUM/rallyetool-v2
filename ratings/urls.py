from django.conf import settings
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework import routers

from . import api, views

app_name = "ratings"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="ratings:view_leaderboard"), name="main-view"),
    path("dashboard/", RedirectView.as_view(pattern_name="ratings:view_leaderboard"), name="dashboard"),
    path("leaderboard/", views.leaderboard, name="view_leaderboard"),
    path(
        "ratings/",
        include(
            [
                path("list/", views.list_ratings, name="list_ratings"),
                path("add/", views.add_rating, name="add_rating"),
                path("edit/<int:rating_pk>/", views.edit_rating, name="edit_rating"),
                path("del/<int:rating_pk>/", views.del_rating, name="del_rating"),
            ],
        ),
    ),
]
if settings.API:
    router = routers.DefaultRouter()
    router.register(r"teams", api.TeamsViewSet, basename="Group")
    urlpatterns += [
        # api
        path("api/", include(router.urls)),
        path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    ]
