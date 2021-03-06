# Generated by Django 3.2.7 on 2021-10-23 00:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ratings", "0009_alter_group_name"),
        ("common", "0004_auto_20211015_0803"),
    ]

    operations = [
        migrations.AddField(
            model_name="settings",
            name="welcome_text",
            field=models.TextField(
                blank=True,
                default="",
                verbose_name="Introductory Text displayed on the landingpage. "
                "Full HTML styling is availible. Disabled if blank.",
            ),
        ),
        migrations.AlterField(
            model_name="settings",
            name="scavenger_hunt_station",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="ratings.station",
                verbose_name="Scavenger hunt station. Scavenger hunt is disabled if blank.",
            ),
        ),
        migrations.AlterField(
            model_name="settings",
            name="station_rating_avialible",
            field=models.BooleanField(default=False, verbose_name="Stations can rate groups"),
        ),
    ]
