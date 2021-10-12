from typing import List

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from django import forms
from django.utils.translation import ugettext_lazy as _

from common.forms import SemesterBasedModelForm
from common.models import Settings
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
                "<li>Only alphanumeric characters, @#$€<>%^&+=_-, space and äöüß are allowed.</li>"
                "<li>Minimum of 4 characters</li>"
                "<li>Maximum of 30 characters</li>"
                "</ul>",
            ),
        }


class CaptchaGroupForm(GroupForm):
    _settings: Settings = Settings.load()
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(attrs={"required_score": _settings.recaptcha_required_score}),
        public_key=_settings.recaptcha_public_key,
        private_key=_settings.recaptcha_private_key,
    )

    class Meta(GroupForm.Meta):
        fields: List[str] = ["name", "captcha"]
