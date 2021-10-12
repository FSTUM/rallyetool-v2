import random
from subprocess import run  # nosec: used for flushing the db

import django.utils.timezone
import lorem
from django.contrib.auth import get_user_model
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


def showroom_fixture_state_no_confirmation():  # nosec: this is only used in a fixture
    run(["python3", "manage.py", "flush", "--noinput"], check=True)

    # user
    _generate_superuser_frank()

    # app common
    semesters = _generate_semesters()

    # app ratings
    _generate_groups(semesters)
    _generate_stations()
    _generate_ratings()


def _generate_ratings():  # nosec: this is only used in a fixture
    groups = ratings_m.Group.objects.all()
    stations = ratings_m.Station.objects.all()

    for group in groups:
        if random.choice((True, True, True, True, False)):
            for station in stations:
                if random.choice((True, False)):
                    points = random.randint(0, 10)
                    ratings_m.Rating.objects.create(
                        station=station,
                        group=group,
                        points=points,
                    )


def _generate_stations():  # nosec: this is only used in a fixture
    users = list(get_user_model().objects.all())
    random.shuffle(users)
    for _ in range(1, random.randint(10, 20)):
        user = None
        if random.choice((True, True, False)) and users:
            user = users.pop()
        ratings_m.Station.objects.create(
            name=lorem.sentence(),
            location_description=lorem.sentence(),
            longitude=11.671 + random.choice((1, -1)) * random.randint(0, 1000) / 1000 / 500,
            latitude=48.265 + random.choice((1, -1)) * random.randint(0, 1000) / 1000 / 500,
            user=user,
        )


def _generate_groups(semesters):  # nosec: this is only used in a fixture
    for semester in semesters:
        for i in range(1, random.randint(21, 100)):
            ratings_m.Group.objects.create(
                semester=semester,
                name=f"Group {i}",
            )


def _generate_superuser_frank():  # nosec: this is only used in a fixture
    return get_user_model().objects.create(
        username="frank",
        password="pbkdf2_sha256$216000$DHqZuXE7LQwJ$i8iIEB3qQN+NXMUTuRxKKFgYYC5XqlOYdSz/0om1FmE=",
        first_name="Frank",
        last_name="Elsinga",
        is_superuser=True,
        is_staff=True,
        is_active=True,
        email="elsinga@fs.tum.de",
        date_joined=django.utils.timezone.make_aware(datetime.today()),
    )


def _generate_semesters():
    semester1 = common_m.Semester.objects.create(semester="WS", year=2019)  # legacy data that should not be shown
    semester2 = common_m.current_semester()
    return semester1, semester2
