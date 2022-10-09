# Generated by Django 4.1 on 2022-10-09 21:46

from django.db import migrations


def drop_all_duplicate_rs3groups(apps, _):
    RatingScheme3Group = apps.get_model("ratings", "ratingscheme3group")
    groups = set()
    for group in RatingScheme3Group.objects.all():
        key = (group.rating_scheme, group.handicap)
        if key in groups:
            group.delete()
        else:
            groups.add(key)


class Migration(migrations.Migration):
    dependencies = [
        ('ratings', '0013_alter_ratingscheme3group_unique_together'),
    ]

    operations = [
        migrations.RunPython(drop_all_duplicate_rs3groups),
    ]
