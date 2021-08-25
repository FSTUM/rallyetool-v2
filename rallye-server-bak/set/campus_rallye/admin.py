from django.contrib import admin
from .models import Laufgruppe, Bewertung, Stand
# Register your models here.

admin.site.register(Laufgruppe)
admin.site.register(Bewertung)
admin.site.register(Stand)