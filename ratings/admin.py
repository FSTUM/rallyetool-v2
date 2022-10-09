from django.contrib import admin

from .models import Group, Rating, Station, RatingScheme1, RatingScheme2, RatingScheme3, RatingScheme3Group

admin.site.register(Group)
admin.site.register(Rating)
admin.site.register(Station)
admin.site.register(RatingScheme1)
admin.site.register(RatingScheme2)
admin.site.register(RatingScheme3)
admin.site.register(RatingScheme3Group)
