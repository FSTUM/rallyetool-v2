from modeltranslation.translator import TranslationOptions, translator

from ratings.models import Station


class StationTranslationOptions(TranslationOptions):
    fields = ("name", "location_description", "station_game_instructions", "setup_instructions", "scoring_instructions")
    required_languages = ("en", "de")


translator.register(Station, StationTranslationOptions)
