from django.contrib.auth import get_user_model
from django.shortcuts import render

from ratings.models import Group, Rating


class InvalidUpdate(Exception):
    pass


#########################
#  Challenges Overview ##
#########################
def challenges(request):
    return render(request, "challenges/challenges-overview.html")


#########################
#   Challenges Common  ##
#########################
def rate_team(team, station, points):
    try:
        rating = Rating.objects.get(gr_id=team, station=station)
        # If team already handed in solution, but new solution is better
        if points > rating.points:
            team.total_points -= rating.points
            team.total_points += points
            team.save()
            rating.points = points
            rating.save()
        # If team already handed in solution, but new solution is worse
        elif points < rating.points:
            raise InvalidUpdate
    # If team did not hand in solution yet
    except Rating.DoesNotExist:
        rating = Rating(gr_id=team, station=station, points=points)
        rating.save()
        team.total_points += points
        team.save()


#########################
#   Crypto Challenge   ##
#########################
def validate_crypto_request(request):
    team_str = request.POST["group"]
    answer = request.POST["decrypted_answer"]
    try:
        team = Group.objects.get(group_number=int(team_str))
    except ValueError as error:
        raise Group.DoesNotExist from error
    return team, answer


def score_crypto_answer(answer):
    points = 0
    if "Neuschwanstein" in answer:
        points += 10
    if "47.5574" in answer or "47,5574" in answer:
        points += 3
    if "10.7494" in answer or "10,7494" in answer:
        points += 3
    return 10 if points > 10 else points


def crypto(request):
    station = get_user_model().objects.get(username="crypto")
    context = {}
    if request.method == "POST":
        try:
            team, answer = validate_crypto_request(request)
            points = score_crypto_answer(answer)
            rate_team(team, station, points)
            context["points"] = points
            context["challenge"] = "Crypto Challenge"
            return render(request, "challenges/challenge-completed.html", context)
        except Group.DoesNotExist:
            context["message"] = "Team does not exist"
            return render(request, "challenges/crypto-challenge.html", context)
        except InvalidUpdate:
            context["message"] = "This team already handed in a solution that scored higher."
            return render(request, "challenges/crypto-challenge.html", context)
    else:
        return render(request, "challenges/crypto-challenge.html", context)


#########################
#  Services Challenge  ##
#########################
def validate_online_services_request(request):
    team_str = request.POST["group"]
    try:
        return Group.objects.get(group_number=int(team_str))
    except ValueError as error:
        raise Group.DoesNotExist from error


def score_online_services_answers(request):
    # TODO: Exclude in File, so that questions and answers can be changed dynamically
    valid_answers = {
        "tumonline": ["6"],
        "moodle": ["Atto HTML Editor"],
        "jitsi": ["meet.lrz.de"],
        "element": ["matrix.tum.de"],
        "library": ["11"],
        "fachschaft": ["Golden Chalk"],
        "asta": ["diversity@fs.tum.de", "queer@fs.tum.de"],
        "email": ["mail.tum.de"],
        "gitlab": ["AM/TUMlatex"],
        "confluence": ["15.05.2020"],
    }
    points = 0
    for category, answer in valid_answers.items():
        if request.POST[category] in answer:
            points += 1
    return points


def online_services(request):
    station = get_user_model().objects.get(username="online_services")
    context = {}
    if request.method == "POST":
        try:
            team = validate_online_services_request(request)
            points = score_online_services_answers(request)
            rate_team(team, station, points)
            context["points"] = points
            context["challenge"] = "Online Services"
            return render(request, "challenges/challenge-completed.html", context)
        except Group.DoesNotExist:
            context["message"] = "Team does not exist"
            return render(request, "challenges/online-services.html", context)
        except InvalidUpdate:
            context["message"] = "This team already handed in a solution that scored higher."
            return render(request, "challenges/online-services.html", context)
    return render(request, "challenges/online-services.html", context)
