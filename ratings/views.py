from typing import Callable

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.forms import forms
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _

from common.models import Settings
from common.views import AuthWSGIRequest, rallye_login_required

from .forms import EditRatingForm, RatingForm
from .models import Group, Rating, Station

user_has_stand_required: Callable = user_passes_test(lambda u: bool(u.station))  # type: ignore


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
        form.save()
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
    messages.warning(request, _("Deletion is permanent."))

    if request.user.station != rating.station:
        return HttpResponseForbidden(_("You cant delete ratings of stations that are not your own"))

    form = forms.Form(request.POST or None)
    if form.is_valid():
        rating.delete()
        return redirect("ratings:list_ratings")
    context = {"form": form, "rating": rating}
    return render(request, "ratings/rating/del_rating.html", context)
