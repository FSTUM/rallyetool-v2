"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import ratings.views as ratingsviews

urlpatterns = [
    path('adminnurfueruns/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', ratingsviews.results, name='results'), 
    path('ratings/', include('ratings.urls')),
    path('challenges/', include('challenges.urls')),
    #path('signup/', ratingsviews.signup, name='signup')
]