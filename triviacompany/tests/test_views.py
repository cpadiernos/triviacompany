from django.test import TestCase
from django.urls import reverse, resolve

from triviacompany.views import about, how_to_play, portal_redirect
from accounts.models import CustomUser

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

class PortalRedirectViewTests(TestCase):

    def test_portal_redirect_url_maps_to_portal_redirect_name(self):
        url = '/portal-redirect/'
        reversed_name = reverse('portal-redirect')
        self.assertEqual(url, reversed_name)

    def test_reverse_portal_redirect_name_resolves_to_portal_redirect_view(self):
        view = resolve(reverse('portal-redirect'))
        self.assertEqual(view.func, portal_redirect)

    def test_reverse_portal_redirect_name_redirects_to_host_events_page_if_logged_in_as_host(self):
        host = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti',
            is_host=True)
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('portal-redirect')
        response = self.client.get(url)
        redirect_url = reverse('event-occurrence-list-host', kwargs={'username': 'carol'})
        self.assertRedirects(response, redirect_url)

    def test_reverse_portal_redirect_name_redirects_to_public_events_page_if_logged_in_as_other_than_host(self):
        host = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('portal-redirect')
        response = self.client.get(url)
        redirect_url = reverse('event-occurrence-list')
        self.assertRedirects(response, redirect_url)