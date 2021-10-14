import datetime
from typing import TypeVar

from django.core.cache import cache
from django.db import models
from django.http import HttpRequest
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _

from ratings.models import Station

from .settings import SEMESTER_SESSION_KEY

SingletonType = TypeVar("SingletonType", bound="SingletonModel")


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        pass

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    def save(self, *args, **kwargs):
        self.pk = 1  # pylint: disable=invalid-name
        super().save(*args, **kwargs)
        self.set_cache()

    @classmethod
    def load(cls) -> SingletonType:
        obj: SingletonType
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class LoggedModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@deconstructible
class Semester(LoggedModel):
    class Meta:
        unique_together = (("semester", "year"),)
        ordering = ["year", "semester"]

    WINTER = "WS"
    SUMMER = "SS"
    SEMESTER_CHOICES = (
        (WINTER, _("Winter semester")),
        (SUMMER, _("Summer semester")),
    )

    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES, default=WINTER, verbose_name=_("Semester"))

    year = models.PositiveIntegerField(verbose_name=_("Year"))

    def short_form(self) -> str:
        return f"{self.semester}{str(self.year)[2:]}"

    def __str__(self):
        return f"{self.get_semester_display()} {self.year:4}"


def current_semester() -> Semester:
    now = timezone.now()
    year = now.year
    if now < timezone.make_aware(datetime.datetime(year, 5, 1)):
        semester = Semester.SUMMER
    elif now >= timezone.make_aware(datetime.datetime(year, 11, 1)):
        semester = Semester.SUMMER
        year += 1
    else:
        semester = Semester.WINTER
    return Semester.objects.get_or_create(semester=semester, year=year)[0]


def get_semester(request: HttpRequest) -> int:
    sem: int
    try:
        sem = int(request.session[SEMESTER_SESSION_KEY])
    except KeyError:
        sem = current_semester().pk
        request.session[SEMESTER_SESSION_KEY] = sem
    return sem  # noqa: R504


class Settings(SingletonModel, LoggedModel):
    station_registration_availible = models.BooleanField(verbose_name="Stations can be registered", default=False)
    station_rating_avialible = models.BooleanField(verbose_name="Stations rate groups", default=False)

    group_registration_available = models.BooleanField(verbose_name="Groups can be registered", default=True)
    
    #challanges
    scavenger_hunt_secret = models.CharField(max_length=10, default="SET", verbose_name=_("Scavenger hunt secret"))
    scavenger_hunt_station = models.OneToOneField(Station, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("Scavenger hunt station. If not present a warning will be caused (i.e. scavenger hunt wont be availible)"))
    scavenger_hunt_points = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=10)

    # recaptcha
    recaptcha_required_score = models.FloatField(
        verbose_name="reCAPTCHA required score. "
        "(see https://developers.google.com/recaptcha/docs/v3#interpreting_the_score)",
        default=0.5,
    )
    recaptcha_private_key = models.CharField(
        max_length=200,
        default="",
        blank=True,
        verbose_name="reCAPTCHA PRIVATE_KEY",
    )
    recaptcha_public_key = models.CharField(max_length=200, default="", blank=True, verbose_name="reCAPTCHA PUBLIC_KEY")
