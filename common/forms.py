from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from common.models import Semester, Settings
from ratings.models import RegistrationToken


class SemesterBasedForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.semester: Semester = kwargs.pop("semester")
        super().__init__(*args, **kwargs)


class SemesterBasedModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.semester: Semester = kwargs.pop("semester")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(False)
        instance.semester = self.semester
        if commit:
            instance.save()
        return instance


class SettingsForm(SemesterBasedForm, forms.ModelForm):
    class Meta:
        model = Settings
        exclude: list[str] = []

    def save(self, commit=True):
        setting: Settings = super().save(commit=False)
        # if station_registration is active a RegistrationToken should exist. else not
        if setting.station_registration_availible:
            RegistrationToken.objects.get_or_create(semester=self.semester)
        else:
            try:
                token = RegistrationToken.objects.get(semester=self.semester)
                token.delete()
            except ObjectDoesNotExist:
                pass
        if commit:
            setting.save()
        return setting


class NewTutorForm(forms.Form):
    data_protection = forms.BooleanField(
        label=mark_safe(
            _(
                "I agree with the data privacy statement. "
                "(<a href data-bs-toggle='modal' data-bs-target='#dataProtectionModal'>Show</a>)",
            ),
        ),
        required=True,
    )
    username = forms.CharField(
        label=_("Username, you can tell to the organisers"),
        help_text=_(
            "<ul>"
            "<li>Please choose an Username you can tell to the organisers. </li>"
            "<li>4...30 characters.</li>"
            "<li>Letters, digits and @/./+/-/_ only.</li>"
            "</ul>",
        ),
        validators=[
            MinLengthValidator(4),
            MaxLengthValidator(30),
            RegexValidator(
                r"^[A-Za-z0-9@#$€<>%\^&+=_\- äüöß]+$",
                _("Only alphanumeric characters, @#$€<>%%^&+=_-, space and äöüß are allowed"),
            ),
        ],
        required=True,
    )
