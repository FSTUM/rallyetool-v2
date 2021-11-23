import random
from subprocess import run  # nosec: used for flushing the db

import django.utils.timezone
import lorem
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.datetime_safe import datetime

import common.models as common_m
import ratings.models as ratings_m


def showroom_fixture_state():
    confirmation = input(
        "Do you really want to load the showroom fixture? (This will flush the database) [y/n]",
    )
    if confirmation.lower() != "y":
        return
    showroom_fixture_state_no_confirmation()


def showroom_fixture_state_no_confirmation():
    run(["python3", "manage.py", "flush", "--noinput"], check=True)

    # user
    _generate_superusers()

    # app common
    semesters = _generate_semesters()

    # app ratings
    _generate_groups(semesters)
    _generate_stations()
    _generate_ratings()


def _generate_superusers():
    users = [
        ("frank", "130120", "Frank", "Elsinga", "elsinga@example.com"),
        ("password", "username", "Nelson 'Big Head'", "Bighetti", "bighetti@example.com"),
    ]
    for username, password, first_name, last_name, email in users:
        get_user_model().objects.create(
            username=username,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            is_superuser=True,
            is_staff=True,
            is_active=True,
            email=email,
            date_joined=django.utils.timezone.make_aware(datetime.today()),
        )


def _set_scheme(scheme):
    for i in range(1, 11):
        scheme.__setattr__(f"mark_for_{i}p", i * 20 - 19)


def _generate_ratings():
    groups = ratings_m.Group.objects.all()
    stations = ratings_m.Station.objects.all()

    for group in groups:
        if random.choice((True, True, True, True, False)):
            for station in stations:
                if random.choice((True, False)):
                    if station.rating_scheme_choices == 3:  # noqa: SIM114
                        ratings_m.Rating.objects.create(
                            station=station,
                            group=group,
                            value=random.randint(0, 200),
                            handicap=random.randint(4, 7),
                        )
                    elif station.rating_scheme_choices == 2:
                        ratings_m.Rating.objects.create(
                            station=station,
                            group=group,
                            value=random.randint(0, 200),
                        )
                    else:
                        ratings_m.Rating.objects.create(
                            station=station,
                            group=group,
                            points=random.randint(0, 10),
                        )

    # rating_scheme setup
    for station in stations:
        if station.rating_scheme_choices == 3:
            for i in range(4, 8):
                rating_scheme = station.rating_scheme
                rating_scheme_group = ratings_m.RatingScheme3Group(rating_scheme=rating_scheme, handicap=i)
                _set_scheme(rating_scheme_group)
                rating_scheme_group.save(recalculate_points=False)
        if station.rating_scheme_choices == 2:
            _set_scheme(station.rating_scheme)
            station.rating_scheme.save(recalculate_points=False)
        station.rating_scheme.recalculate_points()


def _generate_stations():
    users = list(get_user_model().objects.all())
    random.shuffle(users)
    for _ in range(1, random.randint(10, 20)):
        user = None
        if random.choice((True, True, False)) and users:
            user = users.pop()
        name = lorem.sentence()
        location_description = lorem.sentence()
        setup_instructions = lorem.paragraph()
        station_game_instructions = lorem.paragraph()
        scoring_instructions = lorem.paragraph()
        r_s_number = random.choice((1, 2, 3))
        ratings_m.Station.objects.create(
            name=name,
            name_de=name,
            name_en=name,
            location_description=location_description,
            location_description_de=location_description,
            location_description_en=location_description,
            setup_instructions=setup_instructions,
            setup_instructions_de=setup_instructions,
            setup_instructions_en=setup_instructions,
            station_game_instructions=station_game_instructions,
            station_game_instructions_de=station_game_instructions,
            station_game_instructions_en=station_game_instructions,
            scoring_instructions=scoring_instructions,
            scoring_instructions_de=scoring_instructions,
            scoring_instructions_en=scoring_instructions,
            contact_person=lorem.sentence()[:20],
            setup_tools=lorem.sentence(),
            longitude=11.671 + random.choice((1, -1)) * random.randint(0, 1000) / 1000 / 500,
            latitude=48.265 + random.choice((1, -1)) * random.randint(0, 1000) / 1000 / 500,
            tutor_amount=r_s_number,
            user=user,
            rating_scheme_choices=r_s_number,
        )


def _generate_groups(semesters):
    for semester in semesters:
        for i in range(1, random.randint(21, 100)):
            ratings_m.Group.objects.create(
                semester=semester,
                name=f"Group {i}",
            )


def _generate_semesters():
    semester1 = common_m.Semester.objects.create(semester="WS", year=2019)  # legacy data that should not be shown
    semester2 = common_m.current_semester()
    return semester1, semester2
