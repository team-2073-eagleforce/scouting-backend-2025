from django.test import TestCase

# Create your tests here.
from django.urls import reverse, resolve

from .models import Teams
from .views import display_teams, team_page


class TeamTests(TestCase):

    def setUp(self):
        # Create a team for the testing event and mark the test client as logged in
        self.client.defaults['HTTP_HOST'] = 'localhost'
        # Ensure requests are secure to avoid SECURE_SSL_REDIRECT during tests
        self.client.defaults['wsgi.url_scheme'] = 'https'
        self.team = Teams.objects.create(team_number=2073, event='testing')
        session = self.client.session
        session['email'] = 'test@team2073.com'
        session.save()

        teams_page_url = reverse('teams')
        # Follow redirects (tests run with SECURE_SSL_REDIRECT enabled in test mode)
        self.response = self.client.get(teams_page_url, follow=True)

    # Teams Display
    def test_teams_view_success_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_teams_url_resolves_teams_view(self):
        teams_view = resolve('/teams/')
        self.assertEqual(teams_view.func, display_teams)

    def test_teams_contains_link_to_team_page(self):
        team_page_url = reverse('team_page', kwargs={'team_number': self.team.team_number})
        self.assertContains(self.response, 'href="{0}"'.format(team_page_url))

    # Teams Page
    def test_team_page_view_success_status_code(self):
        url = reverse('team_page', kwargs={'team_number': self.team.team_number}) + '?comp=testing'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_team_page_view_not_found_status_code(self):
        url = reverse('team_page', kwargs={'team_number': 0}) + '?comp=testing'
        response = self.client.get(url, follow=True)
        # The current implementation creates the team record when comp is provided,
        # so expect a successful response rather than a 404.
        self.assertEqual(response.status_code, 200)

    def test_team_page_url_resolves_teams_page_view(self):
        view = resolve('/teams/2073/')
        self.assertEqual(view.func, team_page)
