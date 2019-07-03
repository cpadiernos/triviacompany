from django.test import TestCase
from django.urls import reverse, resolve

from accounts.models import CustomUser, HostProfile
from accounts.views import HostProfileListView, CustomUserUpdate
from accounts.forms import CustomUserUpdateForm

class HostProfileListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        host = HostProfile.objects.create(
            user=user, bio='Carol loves to eat!')

    def test_hosts_url_maps_to_host_profile_list_name(self):
        url = '/hosts/'
        reversed_name = reverse('host-profile-list')
        self.assertEqual(url, reversed_name)

    def test_reverse_host_profile_list_name_resolves_to_host_profile_list_view_view(self):
        view = resolve(reverse('host-profile-list'))
        self.assertEqual(view.func.view_class, HostProfileListView)

    def test_reverse_host_profile_list_name_success_status_code(self):
        url = reverse('host-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_host_profile_list_name_uses_correct_template(self):
        url = reverse('host-profile-list')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'accounts/host_profile_list.html')
        
class CustomUserUpdateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti',
            is_host=True)

    def test_hosts_url_maps_to_host_profile_list_name(self):
        url = '/accounts/carol/'
        reversed_name = reverse('account-update', kwargs={'username': 'carol'})
        self.assertEqual(url, reversed_name)

    def test_reverse_account_update_name_resolves_to_custom_user_upate_view(self):
        view = resolve(reverse('account-update', kwargs={'username': 'carol'}))
        self.assertEqual(view.func.view_class, CustomUserUpdate)

    def test_reverse_account_update_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('account-update', kwargs={'username': 'carol'})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_account_update_name_success_status_code_if_logged_in(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('account-update', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_account_update_name_redirects_to_current_page_after_logging_in(self):
        url = reverse('account-update', kwargs={'username': 'carol'})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)

    def test_reverse_account_update_name_not_found_status_code_if_not_existing_host(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('account-update', kwargs={'username': 'notahost'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_account_update_name_not_found_status_code_if_not_correct_host(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('account-update', kwargs={'username': 'matt'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_account_update_name_contains_custom_user_update_form(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('account-update', kwargs={'username': 'carol'})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, CustomUserUpdateForm)

    def test_reverse_account_update_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('account-update', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'accounts/custom_user_form.html')

    def test_reverse_account_update_name_shows_success_message_after_valid_post(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('account-update', kwargs={'username': 'carol'})
        data = {}
        response = self.client.post(url, data, follow=True)
        self.assertContains(response, 'Your account has been updated!')

    def test_reverse_account_update_name_redirects_to_current_page_after_valid_post(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('account-update', kwargs={'username': 'carol'})
        data = {}
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, url)

    def test_reverse_account_update_name_shows_error_after_invalid_post(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('account-update', kwargs={'username': 'carol'})
        data = {}
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, url)

    def test_custom_user_update_form_csrf(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('account-update', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')