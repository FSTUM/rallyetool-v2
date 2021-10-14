from modeltranslation.translator import TranslationOptions, translator

from ratings.models import Station


class StationTranslationOptions(TranslationOptions):
    fields = ("name", "location_description")
    required_languages = ("en", "de")


translator.register(Station, StationTranslationOptions)
