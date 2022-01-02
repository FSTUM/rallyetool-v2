from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _

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


class NewUserForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email, you want to log in with"),
        help_text=_(
            "<ul>"
            "<li>Please choose an (syntactically valid) email that you can remember. "
            "150 characters or fewer.</li>"
            "<li>The email does not have to belong to you. Use a fake-email.</li>"
            "<li>We dont sent mails to this address.</li>"
            "<li><b>No personally identifying information!</b></li>"
            "</ul>",
        ),
        max_length=150,
        required=True,
    )

    class Meta:
        model = get_user_model()
        fields: list[str] = ["username", "email", "password1", "password2"]
        labels = {"username": _("Username, you can tell to the organisers")}
        help_texts = {
            "username": _(
                "<ul>"
                "<li>Please choose an Username you can tell to the organisers. </li>"
                "<li>150 characters or fewer. Letters, digits and @/./+/-/_ only.</li>"
                "<li><b>No personally identifying information!</b></li>"
                "</ul>",
            ),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if getattr(settings, "AUTHENTICATION_BACKENDS", None) and len(settings.AUTHENTICATION_BACKENDS) > 1:
            user.backend = settings.AUTHENTICATION_BACKENDS[-1]
        if commit:
            user.save()
        return user
