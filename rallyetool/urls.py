from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from django.views.generic import RedirectView

import common.views

urlpatterns = [
    # Auth
    path("logout/", LogoutView.as_view(), name="logout"),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("login/failed/", common.views.login_failed),  # adapt to your app
    # localization
    path("i18n/", include("django.conf.urls.i18n")),
    # common: choose semester and settings
    path("", include("common.urls")),
    # Ratings
    path("ratings/", include("ratings.urls")),
    path("r/", RedirectView.as_view(pattern_name="ratings:register_group")),
    path("register/", RedirectView.as_view(pattern_name="ratings:register_group")),
    # Challenges
    path("challenges/", include("challenges.urls")),
    # Admin
    path("admin/", admin.site.urls),
    # Index
    path("", RedirectView.as_view(pattern_name="ratings:main-view"), name="main-view"),
    # Map
    path("map/", RedirectView.as_view(pattern_name="ratings:overview-map"), name="overview-map"),
    path("m/", RedirectView.as_view(pattern_name="ratings:overview-map")),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
