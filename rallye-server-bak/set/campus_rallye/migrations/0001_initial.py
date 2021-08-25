# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-10 18:56
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bewertung',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('punkte', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
            ],
        ),
        migrations.CreateModel(
            name='Laufgruppe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('laufgruppen_name', models.CharField(max_length=100, unique=True)),
                ('laufgruppen_id', models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Stand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stand_name', models.CharField(max_length=100, unique=True)),
                ('stand_id', models.IntegerField(unique=True)),
                ('token', models.IntegerField(unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='bewertung',
            name='lg_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='campus_rallye.Laufgruppe'),
        ),
        migrations.AddField(
            model_name='bewertung',
            name='st_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='campus_rallye.Stand'),
        ),
    ]
