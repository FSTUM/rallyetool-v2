import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from common.forms import SemesterBasedForm
from ratings.models import Group


class ScavengerForm(SemesterBasedForm):
    group_secret = forms.CharField(
        label=_("Result of the scavenger hunt, you got and want to validate"),
        max_length=10,
        help_text=_(
            "Please enter the scavenger hunt secret you got by running around on the campus here. "
            "Capitalisation and letters not between a-z are ignored.",
        ),
    )
    group = forms.ModelChoiceField(
        label=_("Your groups name"),
        queryset=Group.objects.none(),
        help_text=_(
            "Please select your group here. "
            "If you select another group, the points will be awarded to them, instead you you.",
        ),
    )

    def __init__(self, *args, **kwargs):
        self.secret: str = kwargs.pop("secret")
        super().__init__(*args, **kwargs)
        self.fields["group"].queryset = Group.objects.filter(semester=self.semester).all()

    def clean_group_secret(self):
        group_secret: str = self.cleaned_data["group_secret"]
        if not self.secret.lower() == re.sub(r"[^a-z]", "", self.cleaned_data["group_secret"].lower()):
            raise ValidationError(
                _("The secret %(value)s is invalid"),
                params={"value": group_secret},
                code="invalid_secret",
            )
