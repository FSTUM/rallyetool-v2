from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from .forms import ScavengerForm
from ratings.models import Group, Rating, Station

def scavenger_hunt(request: AuthWSGIRequest) -> HttpResponse:
    setting: Settings = Settings.load()
    if not setting.scavenger_hunt_secret:
        messages.error(request, _("The organisers have not provided a Scavenger hunt secret. Contact Them for more information. This might indicate, that this station is not offered"))
        return redirect("main-view")
    station: Station = setting.scavenger_hunt_station
    if not station:
        messages.warning(request, _("The organisers have not provided a Scavenger hunt station. This might indicate, that this station is not offered."))
        return redirect("main-view")

    form = ScavengerForm(request.POST or None, secret=setting.scavenger_hunt_secret)
    if form.is_valid():
        group: Group = form.cleaned_data["group"]
        (_, created) = Rating.objects.get_or_create(station=station, group=group, defaults={"points": setting.scavenger_hunt_points})
        if not created:
            messages.error(request, _("You have already earned the points for the scavenger hunt. You can’t eat the same food twice. No points have been added"))
            return redirect("main-view")
        messages.success(request, _("Success. {} points have been added to group {}.").format(setting.scavenger_hunt_points, group))
        return redirect("main-view")
    
    context = {
        "max_points": setting.scavenger_hunt_secret,
        "form": form,
    }
    return render(request, "challenges/scavenger_hunt.html", context)

