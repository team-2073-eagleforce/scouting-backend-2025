# Generated migration for adding anchor subjective fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0006_alter_team_match_data_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='team_match_data',
            name='driverRanking',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='team_match_data',
            name='defenseRanking',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='team_match_data',
            name='autoLeave',
            field=models.IntegerField(default=0),
        ),
    ]
