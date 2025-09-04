from django.core.management.base import BaseCommand
from authenticate.models import AuthorizedUser
from constants import AUTHORIZED_EMAIL


class Command(BaseCommand):
    help = 'Setup initial admin users from constants'

    def handle(self, *args, **options):
        for email in AUTHORIZED_EMAIL:
            user, created = AuthorizedUser.objects.get_or_create(email=email)
            if created:
                self.stdout.write(f'Created authorized user: {email}')
            else:
                self.stdout.write(f'User already exists: {email}')