from django import template

from common.models import Settings

register = template.Library()


@register.simple_tag
def get_settings():
    return Settings.load()
