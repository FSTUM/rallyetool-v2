from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.


class Laufgruppe(models.Model):
    laufgruppen_name = models.CharField(max_length=100, default="Laufgruppe")
    laufgruppen_id = models.AutoField(primary_key=True, unique=True)
    total_punkte = models.IntegerField(default=0)
    bester_name = models.BooleanField(default=False)

    def __str__(self):
        return self.laufgruppen_id


class Stand(models.Model):
    stand_name = models.CharField(unique=True, max_length=100)
    stand_nummer = models.IntegerField(unique=True)
    token = models.CharField(primary_key=True, unique=True, max_length=20)

    def __str__(self):
        return self.stand_name


class Bewertung(models.Model):
    lg_id = models.ForeignKey(Laufgruppe)
    st_token = models.ForeignKey(Stand)
    punkte = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)]) # Doesn't work - don't know why...

    def __str__(self):
        return "'{}' | {} Punkte | '{}'.".format(self.lg_id.laufgruppen_name, self.punkte, self.st_token.stand_name)
