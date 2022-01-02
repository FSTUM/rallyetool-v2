import uuid
from abc import abstractmethod
from typing import Union

from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models, transaction
from django.db.models import Sum
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy

from common.models import LoggedModel, Semester


class Group(LoggedModel):
    class Meta:
        unique_together = ["name", "semester"]

    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    name = models.CharField(
        _("Name of your Team"),
        max_length=30,
        help_text=_("Visible on a public leaderboard"),
        validators=[
            MinLengthValidator(4),
            MaxLengthValidator(30),
            RegexValidator(
                r"^[A-Za-z0-9@#$€<>%\^&+=_\- äüöß]+$",
                _("Only alphanumeric characters, @#$€<>%%^&+=_-, space and äöüß are allowed"),
            ),
        ],
    )
    total_points = models.IntegerField(default=0)

    def __repr__(self):
        return f"{str(self.id)} - {self.name}"

    def __str__(self):
        return self.name


class AbstractRatingScheme(LoggedModel):
    class Meta:
        abstract = True

    station = models.OneToOneField("ratings.Station", on_delete=models.CASCADE)

    def recalculate_points(self):
        for rating in self.station.rating_set.all():
            self.rate(rating)

    @abstractmethod
    def rate(self, rating: Union["Rating"]) -> int:
        ...

    # pylint: disable=unused-argument
    @transaction.atomic
    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:  # type: ignore
        result = super().delete(*args, **kwargs)
        if kwargs.pop("recalculate_points", True):
            self.recalculate_points()
        return result  # noqa: R504

    @transaction.atomic
    def save(self, *args, **kwargs) -> None:  # type: ignore
        super().save()
        if kwargs.pop("recalculate_points", True):
            self.recalculate_points()


class SchemeBase(models.Model):
    class Meta:
        abstract = True

    mark_for_10p: int
    mark_for_9p: int
    mark_for_8p: int
    mark_for_7p: int
    mark_for_6p: int
    mark_for_5p: int
    mark_for_4p: int
    mark_for_3p: int
    mark_for_2p: int
    mark_for_1p: int
    # set mark_for_1p to mark_for_10p
    for i in range(1, 11):
        _verbose_name_fstr = ngettext_lazy("Min-value for {points} point", "Min-value for {points} points", i)
        _verbose_name = _verbose_name_fstr.format_map({"points": i})
        locals()[f"mark_for_{i}p"] = models.PositiveIntegerField(null=True, blank=True, verbose_name=_verbose_name)

    def generate_rating_lut(self) -> list[tuple[int, int]]:
        result = []
        for i in range(1, 11):
            if self.__dict__[f"mark_for_{i}p"]:
                result.append((self.__dict__[f"mark_for_{i}p"], self.__dict__[f"mark_for_{i}p"]))
        return result

    def _pretty_scheme(self) -> str:
        rating_lut = self.generate_rating_lut()
        result = []
        for poss_rating, mark_for_x in rating_lut:
            result.append(f"value >= {mark_for_x}\t->\t{poss_rating}p")
        return "\n".join(result)

    def _rate_according_to_scheme(self, rating: "Rating") -> int:
        rating_lut = self.generate_rating_lut()
        for poss_rating, mark_for_x in rating_lut:
            if rating.value is None:
                raise Exception("rating.value should have been existance-checked before")
            if rating.value >= mark_for_x:
                return poss_rating
        return 0


class RatingScheme1(AbstractRatingScheme):
    """Rating of the groups by the tutors is final. No RatingScheme."""

    def rate(self, rating: "Rating") -> int:
        return rating.points

    def __str__(self):
        trans = _("RatingScheme 1 (rating is final. No scheme)")
        return gettext(trans)


class RatingScheme2(AbstractRatingScheme, SchemeBase):
    """Rating of the groups by the tutors is based on a single key."""

    def rate(self, rating: "Rating") -> int:
        if rating.value is None:
            raise Exception(
                f"The value of {rating} is needed for the the {self}",
            )
        rating.points = self._rate_according_to_scheme(rating)
        rating.save()
        return rating.points

    def __repr__(self):
        return f"RatingScheme 2\n{self._pretty_scheme()}"

    def __str__(self):
        trans = _("RatingScheme 2 (rating based on a single key)")
        return gettext(trans)


class RatingScheme3(AbstractRatingScheme):
    """Rating of the groups by the tutors is based on multiple keys (one for each handicap)."""

    def rate(self, rating: "Rating") -> int:
        if rating.handicap is None:
            raise Exception(f"The handicap of {rating} is needed for {self}")
        rs_group: RatingScheme3Group = RatingScheme3Group.objects.get(handicap=rating.handicap, rating_scheme=self)
        return rs_group.rate(rating)

    def __str__(self):
        trans = _("RatingScheme 3 (rating based on multiple keys, one for each handicap)")
        return gettext(trans)


class RatingScheme3Group(LoggedModel, SchemeBase):
    """Rating of the groups by the tutors is based on multiple keys (one for each handicap)."""

    rating_scheme = models.ForeignKey(RatingScheme3, on_delete=models.CASCADE)
    handicap = models.PositiveIntegerField(verbose_name=_("Handicap used for grading. (i.e. group-size)"))

    def rate(self, rating: "Rating") -> int:
        rating_group_info = f"the ratingscheme-group {self} (type={type(self)}; handicap={self.handicap})."
        if rating.value is None:
            raise Exception(f"The value of {rating} is needed for {rating_group_info}")
        if rating.handicap is None:
            raise Exception(f"The handicap of {rating} is needed for {rating_group_info}")
        if rating.handicap != self.handicap:
            raise Exception(f"The handicap of {rating} not the same of for {rating_group_info}")
        rating.points = self._rate_according_to_scheme(rating)
        rating.save()
        return rating.points

    def serialization(self):
        return {
            "pk": self.pk,
            "rating_scheme": self.rating_scheme,
            "handicap": self.handicap,
            "mark_for_10p": self.mark_for_10p,
            "mark_for_9p": self.mark_for_9p,
            "mark_for_8p": self.mark_for_8p,
            "mark_for_7p": self.mark_for_7p,
            "mark_for_6p": self.mark_for_6p,
            "mark_for_5p": self.mark_for_5p,
            "mark_for_4p": self.mark_for_4p,
            "mark_for_3p": self.mark_for_3p,
            "mark_for_2p": self.mark_for_2p,
            "mark_for_1p": self.mark_for_1p,
        }

    @transaction.atomic
    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:  # type: ignore
        poss_problemeatic_ratings = Rating.objects.filter(station=self.rating_scheme.station, handicap=self.handicap)
        if poss_problemeatic_ratings.exists():
            raise models.ProtectedError(
                msg=f"The RatingScheme3Group {self}"
                f" is protected by a Rating including the same handycap from the same station",
                protected_objects=set(poss_problemeatic_ratings),
            )
        result = super().delete(*args, **kwargs)
        if kwargs.pop("recalculate_points", True):
            self.rating_scheme.recalculate_points()
        return result  # noqa: R504

    # pylint: disable-next=unused-argument
    @transaction.atomic
    def save(self, *args, **kwargs) -> None:  # type: ignore
        recalculate_points: bool = kwargs.pop("recalculate_points", True)
        super().save(*args, **kwargs)
        if recalculate_points:
            self.rating_scheme.recalculate_points()

    def __repr__(self):
        return f"{self.__str__()}\n{self._pretty_scheme()}"

    def __str__(self):
        return f"ratingscheme3-group (handycap={self.handicap})"


class Station(LoggedModel):
    # general information (translated)
    name = models.CharField(
        _("Name of the Station"),
        default=_("Station-name unknown"),
        max_length=150,
        help_text=_("Visible to logged in users on the map and to tutors"),
    )
    setup_instructions = models.TextField(
        verbose_name=_("Instructions, how to setup the station."),
        help_text=_("Displayed to the tutor."),
        default="-",
    )
    station_game_instructions = models.TextField(
        verbose_name=_("Instructions, how to conduct a game."),
        help_text=_("Displayed to the tutor."),
        default="-",
    )
    scoring_instructions = models.TextField(
        verbose_name=_("Instructions, how to score a game."),
        help_text=_("Displayed to the tutor."),
        default="-",
    )
    # general information (non-translated)
    contact_person = models.TextField(
        verbose_name=_("Contact Person"),
        help_text=_("Displayed to the tutor."),
        default="-",
    )
    setup_tools = models.TextField(
        verbose_name=_("Utensils/tools needed for this station"),
        help_text=_("Displayed to the tutor."),
        default="-",
    )

    # map
    location_description = models.CharField(
        _("Description of the Station"),
        max_length=500,
        default=_("Location unknown"),
        help_text=_("Visible on the map"),
    )
    longitude = models.FloatField(
        verbose_name=_("Longitude of the station"),
        default=11.671,
        help_text=_("Visible on the map"),
    )
    latitude = models.FloatField(
        verbose_name=_("Latitude of the station"),
        default=48.265,
        help_text=_("Visible on the map"),
    )

    # management
    tutor_amount = models.PositiveSmallIntegerField(verbose_name=_("Amount of tutors needed"), default=2)
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    RATING_SCHEME1 = 1
    RATING_SCHEME2 = 2
    RATING_SCHEME3 = 3
    RATING_SCHEME_CHOICES = (
        (RATING_SCHEME1, _("1 - Rating of the groups by the tutors is final. No scheme.")),
        (RATING_SCHEME2, _("2 - Rating of the groups by the tutors is based on a single key.")),
        (
            RATING_SCHEME3,
            _("3 - Rating of the groups by the tutors is based on multiple keys (one for each handicap)."),
        ),
    )
    rating_scheme_choices = models.PositiveSmallIntegerField(
        verbose_name=_("Rating Scheme"),
        default=1,
        choices=RATING_SCHEME_CHOICES,
    )

    def save(self, *args, **kwargs) -> None:  # type: ignore
        super().save(*args, **kwargs)
        _ = self.rating_scheme

    @property
    def rating_scheme(self) -> Union[RatingScheme1, RatingScheme2, RatingScheme3]:
        if self.rating_scheme_choices == self.RATING_SCHEME1:
            return RatingScheme1.objects.get_or_create(station=self)[0]
        if self.rating_scheme_choices == self.RATING_SCHEME2:
            return RatingScheme2.objects.get_or_create(station=self)[0]
        return RatingScheme3.objects.get_or_create(station=self)[0]

    def __str__(self):
        return gettext(self.name)


class Rating(LoggedModel):
    station = models.ForeignKey(Station, on_delete=models.PROTECT)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    points = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    value = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Value achieved by the group"),
        help_text=_("Needed for the RatingScheme 2 or 3"),
    )
    handicap = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Handicap used for grading. (i.e. group-size)"),
        help_text=_("Needed for the RatingScheme 3"),
    )

    @transaction.atomic
    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:  # type: ignore
        result = super().delete(*args, **kwargs)
        self._update_total_points()
        return result  # noqa: R504

    @transaction.atomic
    def save(self, *args, **kwargs) -> None:  # type: ignore
        super().save(*args, **kwargs)
        self._update_total_points()

    def _update_total_points(self) -> None:
        potential_ratings_points = Rating.objects.filter(group=self.group).values("points")
        total_points = potential_ratings_points.aggregate(total_points=Sum("points"))["total_points"]
        self.group.total_points = total_points
        self.group.save()

    def __str__(self):
        return f"{self.group} ({self.points}) at {self.station}"


class RegistrationToken(LoggedModel):
    semester = models.OneToOneField(Semester, on_delete=models.CASCADE)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"{self.semester}: {self.uuid}"
