from django.test import TestCase
from django.urls import reverse, resolve

from triviacompany.views import about, how_to_play

class AboutViewTests(TestCase):

    def test_about_url_maps_to_about_name(self):
        url = '/about/'
        reversed_name = reverse('about')
        self.assertEqual(url, reversed_name)

    def test_reverse_about_name_resolves_to_about_view(self):
        view = resolve(reverse('about'))
        self.assertEqual(view.func, about)

    def test_reverse_about_name_success_status_code(self):
        url = reverse('about')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_about_name_uses_correct_template(self):
        url = reverse('about')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'about.html')

class HowToPlayViewTests(TestCase):

    def test_how_to_play_url_maps_to_how_to_play_name(self):
        url = '/how-to-play/'
        reversed_name = reverse('how-to-play')
        self.assertEqual(url, reversed_name)

    def test_reverse_how_to_play_name_resolves_to_how_to_play_view(self):
        view = resolve(reverse('how-to-play'))
        self.assertEqual(view.func, how_to_play)

    def test_reverse_how_to_play_name_success_status_code(self):
        url = reverse('how-to-play')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_how_to_play_name_uses_correct_template(self):
        url = reverse('how-to-play')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'how_to_play.html')