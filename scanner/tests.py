from django.test import TestCase

# Create your tests here.
from django.urls import reverse, resolve
from .views import scanner


class ScannerTests(TestCase):

    def setUp(self):
        # Ensure test client presents an allowed host and simulate logged-in session
        self.client.defaults['HTTP_HOST'] = 'localhost'
        # Make requests appear secure so SECURE_SSL_REDIRECT doesn't force https redirects
        self.client.defaults['wsgi.url_scheme'] = 'https'
        session = self.client.session
        session['email'] = 'test@team2073.com'
        session.save()

    def test_scanner_view_success_status_code(self):
        url = reverse('scanner')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_scanner_url_resolves_scanner_view(self):
        view = resolve('/scanner/')
        self.assertEqual(view.func, scanner)
