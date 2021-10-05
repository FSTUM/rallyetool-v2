from typing import Callable, Dict, Union
from uuid import UUID

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import ProtectedError, QuerySet
from django.forms import forms
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from common.forms import NewUserForm
from common.models import get_semester, Semester, Settings
from common.views import AuthWSGIRequest, rallye_login_required, superuser_required

from .forms import EditRatingForm, GroupForm, RatingForm, StationForm
from .models import Group, Rating, RegistrationToken, Station

user_has_stand_required: Callable = user_passes_test(lambda u: bool(u.station))  # type: ignore


def register_group(request: WSGIRequest) -> HttpResponse:
    semester: Semester = get_object_or_404(Semester, pk=get_semester(request))

    form = GroupForm(request.POST or None, semester=semester)
    if form.is_valid():
        group: Group = form.save()
        messages.success(request, _("Registration of group '{}' successful.").format(group.name))
        return redirect("main-view")
    if request.POST:
        messages.error(request, _("Unsuccessful registration. Invalid information."))

    return render(request=request, template_name="registration/register_group.html", context={"form": form})


def leaderboard(request: WSGIRequest) -> HttpResponse:
    groups = Group.objects.order_by("total_points").reverse()
    place_and_groups = []
    if groups:
        previous_min = groups[0].total_points
        last_printed_place = 1
        for counter, group in enumerate(groups):
            if group.total_points < previous_min:
                place_and_groups.append((counter, group))
                last_printed_place = counter
                previous_min = group.total_points
            else:
                place_and_groups.append((last_printed_place, group))

    context = {"results": True, "place_and_groups": place_and_groups}
    return render(request, "ratings/leaderboard.html", context)


@rallye_login_required
@user_has_stand_required
def list_ratings(request: AuthWSGIRequest) -> HttpResponse:
    settings: Settings = Settings.load()
    if not settings.station_rating_avialible:
        messages.error(request, _("The organisers have ended this event."))
    station: Station = request.user.station
    ratings: QuerySet[Rating] = Rating.objects.filter(station=request.user.station).all()

    context = {"ratings": ratings, "station": station}
    return render(request, "ratings/rating/list_ratings.html", context)


@rallye_login_required
@user_has_stand_required
def add_rating(request: AuthWSGIRequest) -> HttpResponse:
    settings: Settings = Settings.load()
    if not settings.station_rating_avialible:
        messages.error(request, _("Unabele to add a Rating. The organisers have ended this event."))
        redirect("main-view")

    station = request.user.station
    form = RatingForm(request.POST or None, station=station)
    if request.POST and form.is_valid():
        rating: Rating = form.save()
        messages.success(request, _("Rating {} was successfully added").format(rating))
        return redirect("ratings:list_ratings")

    context = {"form": form}

    return render(request, "ratings/rating/add_rating.html", context)


@rallye_login_required
@user_has_stand_required
def edit_rating(request: AuthWSGIRequest, rating_pk: int) -> HttpResponse:
    settings: Settings = Settings.load()
    if not settings.station_rating_avialible:
        messages.error(request, _("Unabele to edit a Rating. The organisers have ended this event."))
        redirect("main-view")
    rating = get_object_or_404(Rating, pk=rating_pk)
    form = EditRatingForm(request.POST or None, instance=rating)
    if request.POST and form.is_valid():
        form.save()
        messages.success(request, _("Rating {} was successfully edited").format(rating))
        return redirect("ratings:list_ratings")

    context = {"form": form, "rating": rating}

    return render(request, "ratings/rating/edit_rating.html", context)


@rallye_login_required
@user_has_stand_required
def del_rating(request: AuthWSGIRequest, rating_pk: int) -> HttpResponse:
    settings: Settings = Settings.load()
    if not settings.station_rating_avialible:
        messages.error(request, _("Unabele to delete a Rating. The organisers have ended this event."))
        redirect("main-view")
    rating: Rating = get_object_or_404(Rating, pk=rating_pk)

    if request.user.station != rating.station:
        return HttpResponseForbidden(_("You cant delete ratings of stations that are not your own"))

    form = forms.Form(request.POST or None)
    if form.is_valid():
        rating.delete()
        messages.success(request, _("Rating {} was permanently deleted.").format(rating))
        return redirect("ratings:list_ratings")
    messages.warning(request, _("Deletion is permanent."))
    context = {"form": form, "rating": rating}
    return render(request, "ratings/rating/del_rating.html", context)


@superuser_required
def list_stations(request: AuthWSGIRequest) -> HttpResponse:
    stations: QuerySet[Station] = Station.objects.all()
    context: Dict[str, Union[str, QuerySet[Station]]] = {"stations": stations}
    settings: Settings = Settings.load()
    if settings.station_registration_availible:
        semester_pk: int = get_semester(request)
        registration_token: RegistrationToken = get_object_or_404(RegistrationToken, semester=semester_pk)
        link = reverse(
            "ratings:register_user",
            kwargs={
                "registration_uuid": registration_token.uuid,
                "semester_pk": semester_pk,
            },
        )
        context["registration_link"] = request.build_absolute_uri(link)
    return render(request, "ratings/administration/list_stations.html", context)


@superuser_required
def add_station(request: AuthWSGIRequest) -> HttpResponse:
    form = StationForm(request.POST or None)
    if form.is_valid():
        station: Station = form.save()
        messages.success(request, _("Station {} was successfully added.").format(station))
        return redirect("ratings:list_stations")
    context = {"form": form}
    return render(request, "ratings/administration/add_station.html", context)


@superuser_required
def edit_station(request: AuthWSGIRequest, station_pk: int) -> HttpResponse:
    station: Station = get_object_or_404(Station, pk=station_pk)

    form = StationForm(request.POST or None, instance=station)
    if form.is_valid():
        form.save()
        messages.success(request, _("Station {} was successfully edited.").format(station))
        return redirect("ratings:list_stations")
    context = {"form": form, "station": station}
    return render(request, "ratings/administration/edit_station.html", context)


@superuser_required
def del_station(request: AuthWSGIRequest, station_pk: int) -> HttpResponse:
    station: Station = get_object_or_404(Station, pk=station_pk)

    form = forms.Form(request.POST or None)
    if form.is_valid():
        try:
            station.delete()
        except ProtectedError as error:
            ratings = error.args[1]
            formatted_ratings = "; ".join([f"{rating.group} ({rating.points}p)" for rating in ratings])
            messages.error(
                request,
                mark_safe(  # nosec: fully defined
                    _(
                        "Unable to delete the station '{}'.<br/>" "It is currently protected by its ratings:<br/>" "{}",
                    ).format(station, formatted_ratings),
                ),
            )
        messages.success(request, _("station {} was permanently deleted.").format(station))
        return redirect("ratings:list_stations")
    messages.warning(request, _("Deletion is permanent."))
    context = {"form": form, "station": station}
    return render(request, "ratings/administration/del_station.html", context)


def register_user(request: WSGIRequest, semester_pk: int, registration_uuid: UUID) -> HttpResponse:
    settings: Settings = Settings.load()
    if not settings.station_registration_availible:
        messages.error(
            request,
            _(
                "User Registration is disabeled in the settings. "
                "Please contact the organisers if you think that this is an error.",
            ),
        )
        return redirect("main-view")
    get_object_or_404(RegistrationToken, uuid=registration_uuid, semester=semester_pk)
    get_object_or_404(Semester, pk=semester_pk)

    form = NewUserForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, _("Registration successful."))
        return redirect("main-view")
    if request.POST:
        messages.error(request, _("Unsuccessful registration. Invalid information."))

    return render(request=request, template_name="registration/register_user.html", context={"form": form})
