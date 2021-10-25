import uuid
from abc import abstractmethod
from typing import Dict, List, Tuple, Union

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
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

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

    @transaction.atomic
    def delete(self, *args, **kwargs) -> Tuple[int, Dict[str, int]]:  # type: ignore
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

    mark_for_10p = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Min-value for 10 points"))
    mark_for_9p = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Min-value for 9 points"))
    mark_for_8p = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Min-value for 8 points"))
    mark_for_7p = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Min-value for 7 points"))
    mark_for_6p = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Min-value for 6 points"))
    mark_for_5p = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Min-value for 5 points"))
    mark_for_4p = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Min-value for 4 points"))
    mark_for_3p = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Min-value for 3 points"))
    mark_for_2p = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Min-value for 2 points"))
    mark_for_1p = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Min-value for 1 point"))

    def generate_rating_lut(self) -> List[Tuple[int, int]]:
        result = []
        if self.mark_for_10p:
            result.append((10, self.mark_for_10p))
        if self.mark_for_9p:
            result.append((9, self.mark_for_9p))
        if self.mark_for_8p:
            result.append((8, self.mark_for_8p))
        if self.mark_for_7p:
            result.append((7, self.mark_for_7p))
        if self.mark_for_6p:
            result.append((6, self.mark_for_6p))
        if self.mark_for_5p:
            result.append((5, self.mark_for_5p))
        if self.mark_for_4p:
            result.append((4, self.mark_for_4p))
        if self.mark_for_3p:
            result.append((3, self.mark_for_3p))
        if self.mark_for_2p:
            result.append((2, self.mark_for_2p))
        if self.mark_for_1p:
            result.append((1, self.mark_for_1p))
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
        return ugettext(trans)


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
        return ugettext(trans)


class RatingScheme3(AbstractRatingScheme):
    """Rating of the groups by the tutors is based on multiple keys (one for each handicap)."""

    def rate(self, rating: "Rating") -> int:
        if rating.handicap is None:
            raise Exception(f"The handicap of {rating} is needed for {self}")
        rs_group: RatingScheme3Group = RatingScheme3Group.objects.get(handicap=rating.handicap, rating_scheme=self)
        return rs_group.rate(rating)

    def __str__(self):
        trans = _("RatingScheme 3 (rating based on multiple keys, one for each handicap)")
        return ugettext(trans)


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
    def delete(self, *args, **kwargs) -> Tuple[int, Dict[str, int]]:  # type: ignore
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

    @transaction.atomic
    def save(self, *args, **kwargs) -> None:  # type: ignore
        super().save()
        if kwargs.pop("recalculate_points", True):
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
        return ugettext(self.name)


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
    def delete(self, *args, **kwargs) -> Tuple[int, Dict[str, int]]:  # type: ignore
        result = super().delete(*args, **kwargs)
        self._update_total_points()
        return result  # noqa: R504

    @transaction.atomic
    def save(self, *args, **kwargs) -> None:  # type: ignore
        super().save()
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
