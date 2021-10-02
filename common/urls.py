from django.urls import include, path

from common import views

app_name = "common"
urlpatterns = [
    path("semester/", views.set_semester, name="set_semester"),
    path(
        "settings/",
        include(
            [
                path("edit/", views.edit_settings, name="edit_settings"),
            ],
        ),
    ),
]
