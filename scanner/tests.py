from django.test import TestCase

# Create your tests here.
from django.urls import reverse, resolve
from .views import scanner


class ScannerTests(TestCase):

    def test_scanner_view_success_status_code(self):
        url = reverse('scanner')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_scanner_url_resolves_scanner_view(self):
        view = resolve('/scanner/')
        self.assertEquals(view.func, scanner)
