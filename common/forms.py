from typing import List

from django import forms

from common.models import Settings


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        exclude: List[str] = []
