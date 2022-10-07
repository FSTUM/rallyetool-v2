from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext as _

from common.forms import SemesterBasedModelForm
from ratings.models import Group, Rating, RatingScheme2, RatingScheme3, RatingScheme3Group, Station


class EditRatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields: list[str] = ["points"]


class RatingForm(SemesterBasedModelForm):
    class Meta:
        model = Rating
        fields: list[str] = ["group", "points"]

    def __init__(self, *args, **kwargs):
        self.station: Station = kwargs.pop("station")
        super().__init__(*args, **kwargs)
        prohibited_groups = self.station.rating_set.values_list("group__pk", flat=True)
        groups = (
            Group.objects.filter(semester=self.semester).exclude(pk__in=prohibited_groups).values_list("pk", "name")
        )
        self.fields["group"].choices = groups

    def save(self, commit=True):
        rating: Rating = super().save(commit=False)
        rating.station = self.station
        if commit:
            rating.save()
        return rating


class Rating2Form(RatingForm):
    class Meta:
        model = Rating
        fields: list[str] = ["group", "value"]


class Rating3Form(RatingForm):
    class Meta:
        model = Rating
        fields: list[str] = ["group", "value", "handicap"]


class StationForm(forms.ModelForm):
    class Meta:
        model = Station
        exclude: list[str] = [
            "name",
            "location_description",
            "station_game_instructions",
            "setup_instructions",
            "scoring_instructions",
        ]


class EditStationForm(StationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rating_scheme_choices"].widget.attrs = {"class": "no-automatic-choicejs"}

    def clean_rating_scheme_choices(self):
        rating_scheme_choice: int = self.cleaned_data["rating_scheme_choices"]
        own_ratings = Rating.objects.filter(station=self.instance)
        if rating_scheme_choice == 2:
            showstoppers = own_ratings.filter(value=None)
            if showstoppers:
                raise ValidationError(
                    _(
                        "The groups %(value)s have been rated by the station and "
                        "don't include the filed field 'value'. "
                        "Thus the rating-scheme 2 cannot be selected.",
                    ),
                    params={"value": list(showstoppers.values_list("group__name", flat=True))},
                    code="invalid_rating_scheme_value",
                )
        if rating_scheme_choice == 3:
            showstoppers = own_ratings.filter(Q(handicap=None) | Q(value=None))
            if showstoppers:
                raise ValidationError(
                    _(
                        "The groups %(value)s have been rated by the station and "
                        "don't include the filed field 'handicap' or 'value'. "
                        "Thus the rating-scheme 3 cannot be selected.",
                    ),
                    params={"value": list(showstoppers.values_list("group__name", flat=True))},
                    code="invalid_rating_scheme_value",
                )
        return rating_scheme_choice


class RatingScheme2Form(forms.ModelForm):
    class Meta:
        model = RatingScheme2
        exclude: list[str] = ["station"]


class RatingScheme3GroupForm(forms.ModelForm):
    class Meta:
        model = RatingScheme3Group
        exclude: list[str] = ["rating_scheme"]

    def __init__(self, *args, **kwargs):
        self.rating_scheme: RatingScheme3 = kwargs.pop("rating_scheme")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        rs_group: RatingScheme3Group = super().save(commit=False)
        rs_group.rating_scheme = self.rating_scheme
        if commit:
            rs_group.save()
        return rs_group


class GroupForm(SemesterBasedModelForm):
    class Meta:
        model = Group
        fields: list[str] = ["name"]
        help_texts = {
            "name": _(
                "<ul>"
                "<li>Required.</li>"
                "<li>Only alphanumeric characters, @#$€<>%^&+=_-, space and äöüß are allowed.</li>"
                "<li>Minimum of 4 characters</li>"
                "<li>Maximum of 30 characters</li>"
                "</ul>",
            ),
        }


class JsonStationUpdateForm(forms.Form):
    json_update = forms.JSONField(required=True)
