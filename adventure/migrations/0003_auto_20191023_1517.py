# Generated by Django 2.2.6 on 2019-10-23 22:17

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adventure', '0002_room_items'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='items',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), default=[], size=None),
        ),
    ]
