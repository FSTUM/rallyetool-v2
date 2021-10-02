from django.contrib import admin

from .models import Group, Rating, Station

admin.site.register(Group)
admin.site.register(Rating)
admin.site.register(Station)
