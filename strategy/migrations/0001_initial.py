# Generated by Django 4.2.9 on 2024-04-05 21:13

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PickList_Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(default='testing', max_length=16)),
                ('first_pick', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None)),
                ('second_pick', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None)),
                ('third_pick', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None)),
                ('dn_pick', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None)),
            ],
        ),
    ]
