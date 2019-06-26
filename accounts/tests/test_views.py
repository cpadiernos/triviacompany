from django.test import TestCase
from django.urls import reverse, resolve

from accounts.models import CustomUser, HostProfile
from accounts.views import HostProfileListView

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