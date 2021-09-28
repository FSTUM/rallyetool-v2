from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.parsers import JSONParser

from .models import Group, Rating
from .serializers import TeamSerializer


@login_required(login_url="/accounts/login/")
def rate(request):
    context = {"rate": True}

    if request.method == "POST":

        # Variables of the request
        selected_meth = request.POST["action"]
        group_str = request.POST["group"]
        points_str = request.POST["points"]
        station = request.user
        # Cast the request variables if possible, otherwise return to rating page and display error.
        try:
            group, points = check_values(selected_meth, group_str, points_str)
        except Exception as error:  # pylint: disable=broad-except
            context["error"] = str(error)
            return render(request, "ratings/rate.html", context)

        # Handle the request if variables were inserted properly.
        if request.POST["action"] == "rate":
            # Check whether record in db already exists
            try:
                Rating.objects.get(gr_id=group, station=station)
                context["error"] = (
                    "This group has already been rated by you. "
                    'Please use "update" if you want to change the number of points.'
                )
            except Rating.DoesNotExist:
                rating = Rating(gr_id=group, station=station, points=points)
                rating.save()
                # Update total points of group
                group.total_points += points
                group.save()
                context["message"] = f"You rated group {group} with {points} points!"

        elif request.POST["action"] == "update":
            try:
                rating = Rating.objects.get(gr_id=group, station=station)
                group.total_points -= rating.points
                rating.points = points
                rating.save()
                group.total_points += points
                group.save()
                context["message"] = f"You updated rating of group {group} to {points} points!"
            except Rating.MultipleObjectsReturned:
                context["error"] = "Too many ratings for one group. Contact Flo!"
            except Rating.DoesNotExist:
                context["error"] = 'You did not rate this group yet. Please use "rate" first.'

        elif request.POST["action"] == "delete":
            try:
                rating = Rating.objects.get(gr_id=group, station=station)
                group.total_points -= rating.points
                group.save()
                rating.delete()
                context["message"] = f"You deleted rating of group {group}!"
            except Rating.MultipleObjectsReturned:
                context["error"] = "Too many ratings for one group. Contact Flo!"
            except Rating.DoesNotExist:
                context["error"] = "You did not rate this group yet."

    return render(request, "ratings/rate.html", context)


def results(request):
    context = {"results": True, "groups": Group.objects.order_by("total_points").reverse()}
    return render(request, "ratings/results.html", context)


def signup(request):
    context = {}
    if request.method == "POST":
        group_str = request.POST["groupname"]
        group = Group(group_name=group_str)
        group.save()
        context["message"] = f'You successfully created Group "{group_str}"'
    return render(request, "ratings/signup.html", context)


def crypto_challenge(request):
    context = {"message": ""}
    if request.method == "POST":
        pass

    return render(request, "ratings/crypto-challenge.html", context)


def check_values(meth, group, points=None):
    if meth in ["rate", "update"]:
        if not group or not points:
            raise Exception("Please set both values, group and points!")
        try:
            group_obj = Group.objects.get(group_number=int(group))
            points_int = int(points)
            if not 0 < points_int < 10:
                raise Exception("Points must be between 0 and 10!")
            return group_obj, points_int
        except ValueError as error:
            raise Exception("Group number and points should be numbers!") from error
        except Group.DoesNotExist as error:
            raise Exception(f"Typo! Group {group} does not exist.") from error

    elif meth == "delete":
        if not group:
            raise Exception("Please set the group number!")
        try:
            group_obj = Group.objects.get(group_number=int(group))
            return group_obj, None
        except ValueError as error:
            raise Exception("Group number and points should be numbers!") from error
        except Group.DoesNotExist as error:
            raise Exception(f"Typo! Group {group} does not exist.") from error
    raise Exception("I have no idea where I am...please contact Flo!")


class TeamsViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    queryset = Group.objects.all()
    serializer_class = TeamSerializer

    def get(self, request, format=None):  # pylint: disable=redefined-builtin,unused-argument
        queryset = Group.objects.all().order_by("group_number")
        serializer_class = TeamSerializer(data=queryset)
        return JsonResponse(serializer_class.data, safe=False)

    def post(self, request, format=None):  # pylint: disable=redefined-builtin,unused-argument
        data = JSONParser().parse(request)
        serializer = TeamSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):  # pylint: disable=redefined-builtin,invalid-name,unused-argument
        pass
