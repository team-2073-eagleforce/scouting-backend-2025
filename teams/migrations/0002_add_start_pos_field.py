# teams/migrations/0002_add_start_pos_field.py

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE teams_team_match_data 
            ADD COLUMN IF NOT EXISTS start_pos integer DEFAULT 0;
            """,
            reverse_sql="""
            ALTER TABLE teams_team_match_data 
            DROP COLUMN IF EXISTS start_pos;
            """
        ),
    ]
