# Generated by Django 3.2.7 on 2021-10-05 16:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ratings", "0003_alter_group_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="group",
            name="name",
            field=models.CharField(
                help_text="Visible on a public leaderboard",
                max_length=30,
                validators=[
                    django.core.validators.RegexValidator(
                        "^[A-Za-z0-9@#$€<>%^&+=_- äüö]{4,}$",
                        "Only alphanumeric characters, @#$€<>%^&+=_-, space and äöü are allowed",
                    ),
                ],
                verbose_name="Name of your Team",
            ),
        ),
    ]
