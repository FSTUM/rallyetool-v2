from django.contrib import admin
from django.urls import include, path

import ratings.views as ratingsviews

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", ratingsviews.results, name="results"),
    path("ratings/", include("ratings.urls")),
    path("challenges/", include("challenges.urls")),
    # path('signup/', ratingsviews.signup, name='signup')
]
