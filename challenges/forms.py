from django import forms
from django.contrib.auth.models import Group

class ScavengerForm(forms.Form):
    group_secret = forms.CharField(max_length=10, help_text=_("Please enter the scavenger hunt secret you got by running around on the campus here."))
    group = forms.ModelChoiceField(Group.objects.all(), help_text=_("Please select your group here. If you select another group, the points will be awarded to them, instead you you."))

    def __init__(self, *args, **kwargs) -> None:
        self.secret: str = kwargs.pop("secret")
        super().__init__(*args, **kwargs)

    def clean_group_secret():
        if not self.secret.lower() == self.cleaned_data["group_secret"].lower():
            raise ValidationError(
                _('The secret %(value)s is invalid'),
                params={'value': '42'},
                code="invalid_secret",
            )


