from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# Create your models here.
class Group(models.Model):
    group_name = models.CharField(max_length=500, default="Laufgruppe")
    group_number = models.IntegerField(primary_key=True, unique=True, default=0)
    total_points = models.IntegerField(default=0)
    best_name = models.BooleanField(default=False)

    def __str__(self):
        return f"{str(self.group_number)} - {self.group_name}"


class Rating(models.Model):
    gr_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    station = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    points = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])

    def __str__(self):
        return f"{self.gr_id} - {self.station}"
