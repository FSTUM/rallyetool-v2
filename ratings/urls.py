from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"teams", views.TeamsViewSet, basename="Group")

urlpatterns = [
    path("", views.rate, name="rate"),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("results", views.results, name="results"),
    path("crypto", views.crypto_challenge, name="crypto"),
]
