# Generated by Django 3.2.7 on 2021-10-12 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="settings",
            name="group_registration_available",
            field=models.BooleanField(default=True, verbose_name="Groups can be registered"),
        ),
        migrations.AddField(
            model_name="settings",
            name="recaptcha_private_key",
            field=models.CharField(blank=True, default="", max_length=200, verbose_name="reCAPTCHA PRIVATE_KEY"),
        ),
        migrations.AddField(
            model_name="settings",
            name="recaptcha_public_key",
            field=models.CharField(blank=True, default="", max_length=200, verbose_name="reCAPTCHA PUBLIC_KEY"),
        ),
        migrations.AddField(
            model_name="settings",
            name="recaptcha_required_score",
            field=models.FloatField(
                default=0.5,
                verbose_name="reCAPTCHA required score. "
                "(see https://developers.google.com/recaptcha/docs/v3#interpreting_the_score)",
            ),
        ),
    ]
