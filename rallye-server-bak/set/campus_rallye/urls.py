from django.conf.urls import url
from . import views


app_name ='campus_rallye'
urlpatterns = [
    url(r'^bewertung', views.bewertung, name='bewertung'),
    url(r'^(?P<stand_token>[a-z0-9]+)/$', views.index, name='index'),
]