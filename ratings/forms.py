from typing import List

from django import forms

from common.forms import SemesterBasedModelForm
from ratings.models import Group, Rating, Station


class EditRatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields: List[str] = ["points"]


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields: List[str] = ["group", "points"]

    def __init__(self, *args, **kwargs):
        self.station: Station = kwargs.pop("station")
        super().__init__(*args, **kwargs)
        prohibited_groups = self.station.rating_set.values_list("group__pk", flat=True)
        groups = Group.objects.exclude(pk__in=prohibited_groups).values_list("pk", "name")
        self.fields["group"].choices = groups

    def save(self, commit=True):
        rating: Rating = super().save(commit=False)
        rating.station = self.station
        if commit:
            rating.save()
        return rating


class StationForm(forms.ModelForm):
    class Meta:
        model = Station
        exclude: List[str] = []
