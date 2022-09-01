from typing import Any, Callable, Union
from uuid import UUID

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import ProtectedError, QuerySet
from django.forms import forms, formset_factory
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from common.forms import NewTutorForm
from common.models import get_semester, Semester, Settings
from common.views import AuthWSGIRequest, rallye_login_required, superuser_required

from .forms import (
    EditRatingForm,
    EditStationForm,
    GroupForm,
    JsonStationUpdateForm,
    Rating2Form,
    Rating3Form,
    RatingForm,
    RatingScheme2Form,
    RatingScheme3GroupForm,
    StationForm,
)
from .models import Group, Rating, RatingScheme3, RatingScheme3Group, RegistrationToken, Station

user_has_stand_required: Callable = user_passes_test(lambda u: bool(u.station))  # type: ignore


def register_group(request: WSGIRequest) -> HttpResponse:
    settings: Settings = Settings.load()
    if not settings.group_registration_available:
        messages.error(
            request,
            _("Registration of new groups is closed. Contact the Organisers if you think this is a mistake."),
        )
        return redirect("main-view")
    semester: Semester = get_object_or_404(Semester, pk=get_semester(request))

    form = GroupForm(request.POST or None, semester=semester)
    if form.is_valid():
        group_name = form.cleaned_data["name"]
        poss_matching_groups = list(Group.objects.filter(name__iexact=group_name))
        if poss_matching_groups:
            if len(poss_matching_groups) > 1:
                similar_groups = str(group.name for group in poss_matching_groups)
            else:
                similar_groups = poss_matching_groups[0].name
            messages.error(
                request,
                _(
                    "Registration of group '{group_name}' failed. "
                    "A group with a very similar name already exists. "
                    "The contender is: {similar_groups}",
                ).format(
                    {"group_name": group_name, "similar_groups": similar_groups},
                ),
            )
            return redirect("ratings:register_group")
        group: Group = form.save()
        messages.success(request, _("Registration of group '{}' successful.").format(group.name))
        return redirect("main-view")
    if request.POST:
        messages.error(request, _("Unsuccessful registration. Invalid information."))

    return render(request=request, template_name="registration/register_group.html", context={"form": form})


def leaderboard(request: WSGIRequest) -> HttpResponse:
    semester: Semester = get_object_or_404(Semester, pk=get_semester(request))
    groups = list(Group.objects.filter(semester=semester).order_by("total_points").reverse())
    place_and_groups = []
    if groups:
        first = groups.pop(0)
        place_and_groups.append((1, first))

        previous_min = first.total_points
        last_printed_place = 1
        for counter, group in enumerate(groups):
            if group.total_points < previous_min:
                # +2 because of 0 based index and because we have popped one already
                place_and_groups.append((counter + 2, group))
                last_printed_place = counter + 2
                previous_min = group.total_points
            else:
                place_and_groups.append((last_printed_place, group))

    context = {"place_and_groups": place_and_groups}
    return render(request, "ratings/leaderboard.html", context)


@rallye_login_required
@user_has_stand_required
def list_ratings(request: AuthWSGIRequest) -> HttpResponse:
    settings: Settings = Settings.load()
    if not settings.station_rating_avialible:
        messages.error(request, _("The organisers have ended this event."))
    station: Station = request.user.station
    ratings: QuerySet[Rating] = Rating.objects.filter(station=station).all()

    context = {"ratings": ratings, "station": station}
    return render(request, "ratings/rating/list_ratings.html", context)


@rallye_login_required
@user_has_stand_required
def add_rating(request: AuthWSGIRequest) -> HttpResponse:
    settings: Settings = Settings.load()
    if not settings.station_rating_avialible:
        messages.error(request, _("Unable to add a Rating. The organisers have ended this event."))
        return redirect("main-view")

    station = request.user.station

    form_lut = {2: Rating2Form, 3: Rating3Form}
    form_class = form_lut.get(station.rating_scheme_choices, RatingForm)
    form = form_class(request.POST or None, station=station)

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
        messages.error(request, _("Unable to edit a Rating. The organisers have ended this event."))
        return redirect("main-view")
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
        messages.error(request, _("Unable to delete a Rating. The organisers have ended this event."))
        return redirect("main-view")
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
    context: dict[str, Union[str, QuerySet[Station]]] = {"stations": stations}
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

    form = EditStationForm(request.POST or None, instance=station)
    if form.is_valid():
        form.save()
        messages.success(request, _("Station {} was successfully edited.").format(station))
        return redirect("ratings:list_stations")
    messages.info(
        request,
        _(
            "If you want to increment the rating-scheme, make sure that no prior ratings exist. "
            "(highter number schemes require more information)",
        ),
    )
    context = {"form": form, "station": station}
    return render(request, "ratings/administration/edit_station.html", context)


@superuser_required
def sanitise_stations(request: AuthWSGIRequest) -> HttpResponse:
    stations: list[Station] = list(Station.objects.exclude(user=None).all())

    form = forms.Form(request.POST or None)
    if form.is_valid():
        for station in stations:
            station.user = None
            station.save()

        messages.success(
            request,
            _("The users of the stations {} have been permanently removed from their stations.").format(
                stations,
            ),
        )
        return redirect("ratings:list_stations")
    messages.warning(
        request,
        _("Removing people from their stations is permanent. Manually re-adding them is tedious."),
    )
    context = {"form": form, "stations": stations}
    return render(request, "ratings/administration/sanitise_stations.html", context)


@superuser_required
def import_stations(request: AuthWSGIRequest) -> HttpResponse:
    form = JsonStationUpdateForm(request.POST or None)
    if form.is_valid():
        json_update = form.cleaned_data["json_update"]
        if not isinstance(json_update, list):
            messages.error(request, _("json is not of type `list[dict[str, Union[int, float, str]]]`"))
            return redirect("ratings:import_stations")
        for update in json_update:
            if not isinstance(update, dict) or not update:
                messages.error(request, _("json is not of type `list[dict[str, Union[int, float, str]]]`"))
                return redirect("ratings:import_stations")
            if "pk" not in update:
                station: Station = Station.objects.create()
            else:
                station = Station.objects.get_or_create(pk=update.pop("pk"))[0]
            unpacked_update = update.items()
            for key, value in unpacked_update:
                if not isinstance(value, (float, int, str)):
                    messages.error(request, _("json is not of type `list[dict[str, Union[int, float, str]]]`"))
                    return redirect("ratings:import_stations")
                station.__setattr__(key, value)
            station.save()
        messages.success(request, _("All updates have been successfully written"))
        return redirect("ratings:import_stations")
    context = {"form": form}
    messages.warning(
        request,
        _(
            "Importing is risky. Overriding with this import method is non-reversible. "
            "Do this only if you have made an export bevore and and are shure what you are doing.",
        ),
    )
    return render(request, "ratings/administration/import_stations.html", context)


# pylint: disable=unused-argument
@superuser_required
def export_stations(request: AuthWSGIRequest) -> HttpResponse:
    stations_qs = Station.objects.all()
    stations: list[dict[str, Union[int, float, str]]] = [_serialise_station(station) for station in stations_qs]

    return JsonResponse(stations, safe=False, json_dumps_params={"indent": 4})


# pylint: enable=unused-argument


def _serialise_station(station: Any) -> dict[str, Union[int, float, str]]:
    return {
        "pk": station.pk,
        "name_de": station.name_de,
        "name_en": station.name_en,
        "setup_instructions_de": station.setup_instructions_de,
        "setup_instructions_en": station.setup_instructions_en,
        "station_game_instructions_de": station.station_game_instructions_de,
        "station_game_instructions_en": station.station_game_instructions_en,
        "scoring_instructions_de": station.scoring_instructions_de,
        "scoring_instructions_en": station.scoring_instructions_en,
        "contact_person": station.contact_person,
        "setup_tools": station.setup_tools,
        "location_description_de": station.location_description_de,
        "location_description_en": station.location_description_en,
        "longitude": station.longitude,
        "latitude": station.latitude,
        "tutor_amount": station.tutor_amount,
    }


@superuser_required
def del_station(request: AuthWSGIRequest, station_pk: int) -> HttpResponse:
    station: Station = get_object_or_404(Station, pk=station_pk)

    form = forms.Form(request.POST or None)
    if form.is_valid():
        try:
            station.delete()
        except ProtectedError as error:
            ratings = error.args[1]
            formatted_ratings: str = "; ".join([f"{rating.group} ({rating.points}p)" for rating in ratings])
            messages.error(
                request,
                mark_safe(  # nosec: fully defined
                    _(
                        "Unable to delete the station '{station}'.<br/>"
                        "It is currently protected by its ratings:<br/>"
                        "{formatted_ratings}",
                    ).format_map({"station": station, "formatted_ratings": formatted_ratings}),
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

    if django_settings.USE_KEYCLOAK:
        from django_compref_keycloak.decorators import is_tum_shibboleth  # pylint: disable=import-outside-toplevel

        if not request.user.is_authenticated:
            return redirect(f"/oidc/authenticate/?next={request.path}")
        if not is_tum_shibboleth(request.user):
            return redirect(f"/oidc/logout/?next={request.path}")
    else:
        messages.warning(request, "Skipping the shibboleth check for registration in dev-mode")

    form = NewTutorForm(request.POST or None)
    if form.is_valid():
        username: str = form.cleaned_data["username"]
        request.user.username = username
        request.user.save()
    elif request.POST:
        messages.error(request, _("Unsuccessful registration. Invalid information."))

    if not request.user.username.endswith("@shibboleth.tum.de"):
        # the entire point of the further flow is, to ensure, that the user has a readable username
        messages.success(request, _("Registration successful."))
        return redirect("main-view")

    return render(request, "registration/register_user.html", {"form": form})


def overview_map(request: WSGIRequest) -> HttpResponse:
    stations: list[Station] = list(Station.objects.all())
    return render(request, "registration/map.html", {"stations": stations})


@rallye_login_required
@user_has_stand_required
def view_station(request: AuthWSGIRequest, station_pk: int) -> HttpResponse:
    station: Station = get_object_or_404(Station, pk=station_pk)
    return render(request, "ratings/station/view_station.html", {"station": station})


@rallye_login_required
@user_has_stand_required
def manage_rating_scheme(request: AuthWSGIRequest) -> HttpResponse:
    station: Station = request.user.station
    rating_scheme = station.rating_scheme

    context: dict[str, Any] = {"station": station, "rating_scheme": rating_scheme}
    if station.rating_scheme_choices == 2:
        form = RatingScheme2Form(request.POST or None, instance=rating_scheme)
        if form.is_valid():
            form.save()
            messages.success(request, _("RatingScheme2 was successful modified."))
            return redirect("ratings:manage_rating_scheme")
        context["form"] = form
    if station.rating_scheme_choices == 3:
        if not isinstance(rating_scheme, RatingScheme3):
            raise Exception("impossible state")
        rs_groups = [rs.serialization() for rs in RatingScheme3Group.objects.filter(rating_scheme=rating_scheme).all()]
        RatingScheme3GroupFormSet = formset_factory(RatingScheme3GroupForm, extra=1)
        formset = RatingScheme3GroupFormSet(
            request.POST or None,
            initial=rs_groups,
            form_kwargs={"rating_scheme": rating_scheme},
        )
        if formset.is_valid():
            for form in formset:
                form.save()
            messages.success(request, _("RatingScheme3s' Groups were successfully modified."))
            return redirect("ratings:manage_rating_scheme")
        context["formset"] = formset

    return render(request, "ratings/station/rating_scheme/manage_rating_scheme.html", context)
