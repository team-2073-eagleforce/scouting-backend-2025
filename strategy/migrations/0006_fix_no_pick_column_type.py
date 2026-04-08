# Generated manually — convert no_pick from integer[] to jsonb

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strategy', '0005_alter_picklist_data_dn_pick_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE strategy_picklist_data ALTER COLUMN no_pick TYPE jsonb USING to_jsonb(no_pick);",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='picklist_data',
            name='no_pick',
            field=models.JSONField(default=list),
        ),
    ]
