from django.urls import path

from . import views

app_name = "challanges"
urlpatterns = [
    path("scavenger_hunt", views.scavenger_hunt, name="scavenger_hunt"),
]
