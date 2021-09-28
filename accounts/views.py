from django.contrib import auth
from django.shortcuts import redirect, render


def login(request):
    context = {"login": True}
    if request.method == "POST":
        user = auth.authenticate(username=request.POST["username"], password=request.POST["password"])
        if user is not None:
            auth.login(request, user)
            return redirect("rate")
            # return render(request, 'ratings/rate.html', {'login': False})
        context["error"] = "Invalid username or password."
    return render(request, "accounts/login.html", context)


def logout(request):
    if request.method == "POST":
        auth.logout(request)

    return render(request, "accounts/login.html", {"login": True})
