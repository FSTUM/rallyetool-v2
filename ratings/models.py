from typing import Dict, Tuple
import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from common.models import LoggedModel, Semester


class Group(LoggedModel):
    class Meta:
        unique_together = ["name", "semester"]

    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    name = models.CharField(_("Name of your Team"), max_length=20, help_text=_("Visible on a public leaderboard"))
    total_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{str(self.id)} - {self.name}"


class Station(LoggedModel):
    name = models.CharField(_("Name of the Station"), max_length=150, help_text=_("Only internally visible"))
    description = models.CharField(
        _("Description of the Station"),
        max_length=500,
        help_text=_("Only internally visible"),
    )
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Rating(LoggedModel):
    station = models.ForeignKey(Station, on_delete=models.PROTECT)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    points = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])

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
        total_points = Rating.objects.filter(group=self.group).values("points").aggregate(total_points=Sum("points"))
        self.group.total_points = total_points["total_points"]
        self.group.save()

    def __str__(self):
        return f"{self.group} - {self.station}"


class RegistrationToken(LoggedModel):
    semester = models.OneToOneField(Semester, on_delete=models.CASCADE)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
