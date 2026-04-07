from django.db import migrations

SEED_EMAILS = [
    "adrienne.nguyen@team2073.com",
    "chris.luk@team2073.com",
    "praneel.arya@team2073.com",
    "matt.beaudin@team2073.com",
    "stan.chong@team2073.com",
]


def seed_authorized_users(apps, schema_editor):
    AuthorizedUser = apps.get_model('authenticate', 'AuthorizedUser')
    for email in SEED_EMAILS:
        AuthorizedUser.objects.get_or_create(email=email)


def unseed_authorized_users(apps, schema_editor):
    AuthorizedUser = apps.get_model('authenticate', 'AuthorizedUser')
    for email in SEED_EMAILS:
        AuthorizedUser.objects.filter(email=email).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('authenticate', '0002_sitesettings'),
    ]

    operations = [
        migrations.RunPython(seed_authorized_users, reverse_code=unseed_authorized_users),
    ]
