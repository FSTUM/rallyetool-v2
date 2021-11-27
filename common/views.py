from typing import Callable, Optional

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import is_safe_url
from django.utils.translation import gettext as _

from common.models import get_semester, Semester, Settings

from .forms import SettingsForm
from .settings import SEMESTER_SESSION_KEY


class AuthWSGIRequest(WSGIRequest):
    user: User


rallye_login_required: Callable = login_required(login_url="login")
superuser_required: Callable = user_passes_test(lambda u: u.is_superuser)


@rallye_login_required
def set_semester(request: AuthWSGIRequest) -> HttpResponse:
    redirect_url: Optional[str] = request.POST.get("next") or request.GET.get("next")
    if not is_safe_url(url=redirect_url, allowed_hosts=request.get_host()):
        redirect_url = request.META.get("HTTP_REFERER")
        if not is_safe_url(url=redirect_url, allowed_hosts=request.get_host()):
            redirect_url = "/"  # should not happen :)
    if request.method == "POST":
        semester_pk = int(request.POST.get("semester") or -1)  # semester is always present
        try:
            Semester.objects.get(pk=semester_pk)
        except Semester.DoesNotExist:
            pass
        else:
            request.session[SEMESTER_SESSION_KEY] = semester_pk
    return HttpResponseRedirect(redirect_url or "/")


@superuser_required
def edit_settings(request: AuthWSGIRequest) -> HttpResponse:
    semester: Semester = get_object_or_404(Semester, pk=get_semester(request))
    settings: Settings = Settings.load()
    form = SettingsForm(request.POST or None, instance=settings, semester=semester)
    if form.is_valid():
        form.save()
        return redirect("main-view")

    context = {
        "form": form,
    }
    return render(request, "common/settings/edit_settings.html", context)
