from typing import List

from django import forms
from django.utils.translation import ugettext_lazy as _

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


class GroupForm(SemesterBasedModelForm):
    class Meta:
        model = Group
        fields: List[str] = ["name"]
        help_texts = {
            "name": _(
                "<ul>"
                "<li>Required.</li>"
                "<li>Only alphanumeric characters, @#$€<>%^&+=_-, space and äöü are allowed.</li>"
                "<li>Minimum of 4 characters</li>"
                "<li>Maximum of 30 characters</li>"
                "</ul>",
            ),
        }
