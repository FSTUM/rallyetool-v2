from django.urls import path
from . import views

urlpatterns = [
    path('', views.challenges, name='challenges'),
    path('crypto', views.crypto, name='crypto'),
    path('online-services', views.online_services, name='online-services')
]