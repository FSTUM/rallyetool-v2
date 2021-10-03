from typing import List

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist

from common.models import Settings, Semester
from ratings.models import RegistrationToken


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        exclude: List[str] = []

    def __init__(self, *args, **kwargs):
        self.semester: Semester = kwargs.pop("semester")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        settings: Settings = super().save(commit=False)
        # if station_registration is active a RegistrationToken should exist. else not
        if settings.station_registration_availible:
            RegistrationToken.objects.get_or_create(semester=self.semester)
        else:
            try:
                token = RegistrationToken.objects.get(semester=self.semester)
                token.delete()
            except ObjectDoesNotExist:
                pass
        if commit:
            settings.save()
        return settings


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
