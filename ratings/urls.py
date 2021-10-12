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
    path("register/", views.register_group, name="register_group"),
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
    path(
        "administration/",
        include(
            [
                path(
                    "registration/<int:semester_pk>/<uuid:registration_uuid>",
                    views.register_user,
                    name="register_user",
                ),
                path(
                    "station/",
                    include(
                        [
                            path("list/", views.list_stations, name="list_stations"),
                            path("add/", views.add_station, name="add_station"),
                            path("edit/<int:station_pk>/", views.edit_station, name="edit_station"),
                            path("del/<int:station_pk>/", views.del_station, name="del_station"),
                        ],
                    ),
                ),
            ],
        ),
    ),
    path("map/", views.overview_map, name="overview-map"),
]
if settings.API:
    router = routers.DefaultRouter()
    router.register(r"teams", api.TeamsViewSet, basename="Group")
    urlpatterns += [
        # api
        path("api/", include(router.urls)),
        path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    ]
