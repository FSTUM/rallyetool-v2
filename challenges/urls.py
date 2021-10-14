from django.urls import path

from . import views

urlpatterns = [
    path("scavenger_hunt", views.scavenger_hunt, name="scavenger_hunt"),
]
