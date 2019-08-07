import datetime
import shutil

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse, resolve
from django.views.generic import ListView

from accounting.forms import ReimbursementForm
from accounting.models import EventOccurrencePayment, PayStub, Reimbursement
from accounting.views import (
    BelongsToUserInUrlMixin,
    PayStubListViewUser,
    PayStubListViewPastUser,
    PayStubListViewCurrentUser,
    PayStubDetailView,
    ReimbursementListViewUser,
    ReimbursementUpdateView,
    ReimbursementCreateView,
)

from accounts.models import CustomUser, HostProfile
from schedule.models import Event, EventOccurrence

class PayStubDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        pay_stub = PayStub.objects.create(
            user=user,
            pay_date=datetime.date.today())

    def test_pay_stubs_number_url_maps_to_pay_stub_detail_name(self):
        url = '/pay-stubs/1/'
        reversed_name = reverse('pay-stub-detail', kwargs={'pk': 1})
        self.assertEqual(url, reversed_name)

    def test_reverse_pay_stub_detail_name_resolves_to_pay_stub_detail_view(self):
        view = resolve(reverse('pay-stub-detail', kwargs={'pk': 1}))
        self.assertEqual(view.func.view_class, PayStubDetailView)

    def test_reverse_pay_stub_detail_name_success_status_code_if_logged_in(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_pay_stub_detail_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('pay-stub-detail', kwargs={'pk': 1})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_pay_stub_detail_name_redirects_to_current_page_after_logging_in(self):
        url = reverse('pay-stub-detail', kwargs={'pk': 1})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)

    def test_reverse_pay_stub_detail_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'accounting/pay_stub_detail.html')

    def test_reverse_pay_stub_detail_name_not_found_status_code_if_pay_stub_does_not_exist(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-detail', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_pay_stub_detail_name_not_found_status_code_if_not_correct_user(self):
        user_2 = CustomUser.objects.create_user(
            username='matt', password='Ilovemeatballs')
        pay_stub = PayStub.objects.filter(pk=1)
        pay_stub.update(user=user_2)
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class PayStubListViewUserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        host_profile = HostProfile.objects.create(
            user=user,
            base_teams=5, base_rate=50,
            incremental_teams=1, incremental_rate=1)
        event = Event.objects.create(
            start_date=datetime.date.today() - datetime.timedelta(days=7),
            end_date=datetime.date.today() + datetime.timedelta(days=7))
        occurrence = EventOccurrence.objects.create(
            event=event,
            host=user,
            time_started=datetime.time(20,15),
            time_ended=datetime.time(22,15),
            number_of_teams=10)

    def test_pay_stubs_username_url_maps_to_pay_stub_list_user_name(self):
        url = '/pay-stubs/carol/'
        reversed_name = reverse('pay-stub-list-user', kwargs={'username': 'carol'})
        self.assertEqual(url, reversed_name)
        
    def test_reverse_pay_stub_list_user_name_resolves_to_pay_stub_list_view_user(self):
        view = resolve(reverse('pay-stub-list-user', kwargs={'username': 'carol'}))
        self.assertEqual(view.func.view_class, PayStubListViewUser)

    def test_reverse_pay_stub_list_user_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'accounting/pay_stub_list.html')
        
    def test_reverse_pay_stub_list_user_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('pay-stub-list-user', kwargs={'username': 'carol'})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_pay_stub_list_user_name_success_status_code_if_logged_in(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_pay_stub_list_user_name_redirects_to_current_page_after_logging_in(self):
        url = reverse('pay-stub-list-user', kwargs={'username': 'carol'})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)
        
    def test_reverse_pay_stub_list_user_name_not_found_status_code(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-user', kwargs={'username': 'matt'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_pay_stub_list_user_name_includes_only_logged_in_user_pay_stubs(self):
        user_2 = CustomUser.objects.create_user(
            username='matt', password='Ilovemeatballs')
        host_profile_2 = HostProfile.objects.create(
            user=user_2,
            base_teams=5, base_rate=50,
            incremental_teams=1, incremental_rate=1)
        event_2 = Event.objects.create(
            start_date=datetime.date.today() - datetime.timedelta(days=7),
            end_date=datetime.date.today() + datetime.timedelta(days=7))
        occurrence_2 = EventOccurrence.objects.create(
            event=event_2,
            host=user_2,
            time_started=datetime.time(20,15),
            time_ended=datetime.time(22,15),
            number_of_teams=5)
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertContains(response, '$55.00')
        self.assertNotContains(response, '$50.00')

    def test_reverse_pay_stub_list_user_name_contains_link_to_pay_stub_list_current_user_name(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        pay_stub_current_url = reverse('pay-stub-list-current-user', kwargs={'username': 'carol'})
        self.assertContains(response, 'href="{0}"'.format(pay_stub_current_url))

    def test_reverse_pay_stub_list_user_name_contains_link_to_pay_stub_list_past_user_name(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        pay_stub_past_url = reverse('pay-stub-list-past-user', kwargs={'username': 'carol'})
        self.assertContains(response, 'href="{0}"'.format(pay_stub_past_url))
        
    def test_reverse_pay_stub_list_user_name_contains_link_to_pay_stub_detail_name(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        pay_stub_detail_url = reverse('pay-stub-detail', kwargs={'pk': 1})
        self.assertContains(response, 'href="{0}"'.format(pay_stub_detail_url))

class PayStubListViewCurrentUserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        pay_stub = PayStub.objects.create(
            user=user,
            pay_date=datetime.date.today())

    def test_pay_stub_username_current_url_maps_to_pay_stub_list_current_user_name(self):
        url = '/pay-stubs/carol/current/'
        reversed_name = reverse('pay-stub-list-current-user', kwargs={'username': 'carol'})
        self.assertEqual(url, reversed_name)

    def test_reverse_pay_stub_list_current_user_name_resolves_to_pay_stub_list_view_current_user_view(self):
        view = resolve(reverse('pay-stub-list-current-user', kwargs={'username': 'carol'}))
        self.assertEqual(view.func.view_class, PayStubListViewCurrentUser)

    def test_reverse_pay_stub_list_current_user_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-current-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'accounting/pay_stub_list.html')

    def test_reverse_pay_stub_list_current_user_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('pay-stub-list-current-user', kwargs={'username': 'carol'})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_pay_stub_list_current_user_name_success_status_code_if_logged_in(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-current-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_pay_stub_list_current_user_name_redirects_to_current_page_after_logging_in(self):
        url = reverse('pay-stub-list-current-user', kwargs={'username': 'carol'})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)

    def test_reverse_pay_stub_list_current_user_name_not_found_status_code_if_not_correct_user(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-current-user', kwargs={'username': 'matt'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_pay_stub_list_current_user_name_includes_only_logged_in_user_pay_stubs_today_and_in_future(self):
        week_before_today = datetime.date.today() - datetime.timedelta(days=7)
        today = datetime.date.today()
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        week_after_today = datetime.date.today() + datetime.timedelta(days=7)

        user = CustomUser.objects.get(username='carol')
        pay_stub_past = PayStub.objects.create(
            user=user,
            pay_date=week_before_today)
        pay_stub_today = PayStub.objects.create(
            user=user,
            pay_date=today)
        pay_stub_future = PayStub.objects.create(
            user=user,
            pay_date=week_after_today)

        user_2 = CustomUser.objects.create_user(
            username='matt', password='Ilovemeatballs')
        pay_stub_2_past = PayStub.objects.create(
            user=user_2,
            pay_date=yesterday)

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-current-user', kwargs={'username': 'carol'})
        response = self.client.get(url)

        # leading spaces in case test is done at beginning of the month (for months after months with 31 days)
        # i.e. " 1, 2019" should pass, but " 31,2019" should not.
        self.assertNotContains(response, f' {week_before_today.day}, {week_before_today.year}')
        self.assertContains(response, f' {today.day}, {today.year}')
        self.assertContains(response, f' {week_after_today.day}, {week_after_today.year}')
        self.assertNotContains(response, f' {yesterday.day}, {yesterday.year}')

    def test_reverse_pay_stub_list_current_user_name_contains_link_to_pay_stub_list_current_user_name(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-current-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        pay_stub_current_url = reverse('pay-stub-list-current-user', kwargs={'username': 'carol'})
        self.assertContains(response, 'href="{0}"'.format(pay_stub_current_url))

    def test_reverse_pay_stub_list_current_user_name_contains_link_to_pay_stub_list_past_user_name(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-current-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        pay_stub_past_url = reverse('pay-stub-list-past-user', kwargs={'username': 'carol'})
        self.assertContains(response, 'href="{0}"'.format(pay_stub_past_url))
        
    def test_reverse_pay_stub_list_current_user_name_contains_link_to_pay_stub_detail_name(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-current-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        pay_stub_detail_url = reverse('pay-stub-detail', kwargs={'pk': 1})
        self.assertContains(response, 'href="{0}"'.format(pay_stub_detail_url))

class PayStubListViewPastUserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        pay_stub = PayStub.objects.create(
            user=user,
            pay_date=datetime.date.today())

    def test_pay_stub_username_past_url_maps_to_pay_stub_list_past_user_name(self):
        url = '/pay-stubs/carol/past/'
        reversed_name = reverse('pay-stub-list-past-user', kwargs={'username': 'carol'})
        self.assertEqual(url, reversed_name)

    def test_reverse_pay_stub_list_past_user_name_resolves_to_pay_stub_list_view_past_user_view(self):
        view = resolve(reverse('pay-stub-list-past-user', kwargs={'username': 'carol'}))
        self.assertEqual(view.func.view_class, PayStubListViewPastUser)

    def test_reverse_pay_stub_list_past_user_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-past-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'accounting/pay_stub_list.html')

    def test_reverse_pay_stub_list_past_user_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('pay-stub-list-past-user', kwargs={'username': 'carol'})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_pay_stub_list_past_user_name_success_status_code_if_logged_in(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-past-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_pay_stub_list_past_user_name_redirects_to_current_page_after_logging_in(self):
        url = reverse('pay-stub-list-past-user', kwargs={'username': 'carol'})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)

    def test_reverse_pay_stub_list_past_user_name_not_found_status_code_if_not_correct_user(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-past-user', kwargs={'username': 'matt'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_pay_stub_list_past_user_includes_only_logged_in_user_pay_stubs_today_and_in_past(self):
        week_before_today = datetime.date.today() - datetime.timedelta(days=7)
        today = datetime.date.today()
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        week_after_today = datetime.date.today() + datetime.timedelta(days=7)

        user = CustomUser.objects.get(username='carol')
        pay_stub_past = PayStub.objects.create(
            user=user,
            pay_date=week_before_today)
        pay_stub_today = PayStub.objects.create(
            user=user,
            pay_date=today)
        pay_stub_future = PayStub.objects.create(
            user=user,
            pay_date=week_after_today)

        user_2 = CustomUser.objects.create_user(
            username='matt', password='Ilovemeatballs')
        pay_stub_2_past = PayStub.objects.create(
            user=user_2,
            pay_date=yesterday)

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-past-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        # leading spaces in case test is done at end of the month (for months with 31 days)
        # i.e. " 31,2019" should pass, but " 1, 2019" should not.
        self.assertContains(response, f' {week_before_today.day}, {week_before_today.year}')
        self.assertContains(response, f' {today.day}, {today.year}')
        self.assertNotContains(response, f' {week_after_today.day}, {week_after_today.year}')
        self.assertNotContains(response, f' {yesterday.day}, {yesterday.year}')

    def test_reverse_pay_stub_list_past_user_name_contains_link_to_pay_stub_list_current_user_name(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-past-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        pay_stub_current_url = reverse('pay-stub-list-current-user', kwargs={'username': 'carol'})
        self.assertContains(response, 'href="{0}"'.format(pay_stub_current_url))

    def test_reverse_pay_stub_list_past_user_name_contains_link_to_pay_stub_list_past_user_name(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-past-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        pay_stub_past_url = reverse('pay-stub-list-past-user', kwargs={'username': 'carol'})
        self.assertContains(response, 'href="{0}"'.format(pay_stub_past_url))
        
    def test_reverse_pay_stub_list_past_user_name_contains_link_to_pay_stub_detail_name(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pay-stub-list-past-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        pay_stub_detail_url = reverse('pay-stub-detail', kwargs={'pk': 1})
        self.assertContains(response, 'href="{0}"'.format(pay_stub_detail_url))

@override_settings(MEDIA_ROOT='temp_documentation_files')
class ReimbursementCreateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('temp_documentation_files')
        super().tearDownClass()

    def test_reimbursements_new_url_maps_to_reimbursement_create_name(self):
        url = '/reimbursements/new/'
        reversed_name = reverse('reimbursement-create')
        self.assertEqual(url, reversed_name)

    def test_reverse_reimbursement_create_name_resolves_to_reimbursement_create_view(self):
        view = resolve(reverse('reimbursement-create'))
        self.assertEqual(view.func.view_class, ReimbursementCreateView)

    def test_reverse_reimbursement_create_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('reimbursement-create')
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_reimbursement_create_name_success_status_code_if_logged_in(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_reimbursement_create_name_redirects_to_current_page_after_logging_in(self):
        url = reverse('reimbursement-create')
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)

    def test_reverse_reimbursement_update_name_contains_reimbursement_form(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-create')
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, ReimbursementForm)

    def test_reverse_reimbursement_create_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-create')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'accounting/reimbursement_create.html')

    def test_reverse_reimbursement_create_name_form_csrf(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-create')
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_reverse_reimbursement_create_name_valid_post_data(self):
        test_file = SimpleUploadedFile('documentation.txt', b'Beer for $2.50.')
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-create')
        data = {
            'purchase_date': datetime.date.today(),
            'category': 'F/D',
            'description': 'Beer for a regular.',
            'amount': '2.50',
            'documentation': test_file,
        }
        response = self.client.post(url, data)
        user = CustomUser.objects.get(username='carol')
        reimbursement_user = Reimbursement.objects.get(pk=1).user
        self.assertEqual(Reimbursement.objects.all().count(), 1)
        self.assertEqual(reimbursement_user, user)

    def test_reverse_reimbursement_create_name_invalid_post_data_empty_fields(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-create')
        data = {
            'purchase_date': '',
            'category': '',
            'description': '',
            'amount': '',
            'documentation': '',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reimbursement.objects.all().count(), 0)

    def test_reverse_reimbursement_create_name_redirects_to_reimbursement_list_user_name_after_valid_post(self):
        test_file = SimpleUploadedFile('documentation.txt', b'Beer for $2.50.')
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-create')
        data = {
            'purchase_date': datetime.date.today(),
            'category': 'F/D',
            'description': 'Beer for a regular.',
            'amount': '2.50',
            'documentation': test_file,
        }
        response = self.client.post(url, data)
        success_url = reverse('reimbursement-list-user', kwargs={'username': 'carol'})
        self.assertRedirects(response, success_url)

class ReimbursementListViewUserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        reimbursement = Reimbursement.objects.create(
            user=user,
            submission_date=datetime.date.today())

    def test_reimbursements_username_url_maps_to_reimbursement_list_user_name(self):
        url = '/reimbursements/carol/'
        reversed_name = reverse('reimbursement-list-user', kwargs={'username': 'carol'})
        self.assertEqual(url, reversed_name)

    def test_reverse_reimbursement_list_user_name_resolves_to_reimbursement_list_view_user_view(self):
        view = resolve(reverse('reimbursement-list-user', kwargs={'username': 'carol'}))
        self.assertEqual(view.func.view_class, ReimbursementListViewUser)

    def test_reverse_reimbursement_list_user_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-list-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'accounting/reimbursement_list.html')

    def test_reverse_reimbursement_list_user_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('reimbursement-list-user', kwargs={'username': 'carol'})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_reimbursement_list_user_name_success_status_code_if_logged_in(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-list-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_reimbursement_list_user_name_redirects_to_current_page_after_logging_in(self):
        url = reverse('reimbursement-list-user', kwargs={'username': 'carol'})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)

    def test_reverse_reimbursement_list_user_name_not_found_status_code_if_not_correct_user(self):
        user_2 = CustomUser.objects.create_user(
            username='matt', password='Ilovemeatballs')
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-list-user', kwargs={'username': 'matt'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_reimbursement_list_user_name_includes_only_logged_in_user_reimbursements(self):
        day_before_today = datetime.date.today() - datetime.timedelta(days=7)
        today = datetime.date.today()

        user = CustomUser.objects.get(username='carol')
        reimbursement = Reimbursement.objects.get(
            user=user,
            submission_date=today)

        user_2 = CustomUser.objects.create_user(
            username='matt', password='Ilovemeatballs')
        reimbursement_2 = Reimbursement.objects.create(
            user=user_2,
            submission_date=today)

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-list-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertEqual(reimbursement in response.context['reimbursement_list'], True)
        self.assertEqual(reimbursement_2 not in response.context['reimbursement_list'], True)

    def test_reverse_reimbursement_list_user_name_contains_link_to_reimbursement_create_name(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-list-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        reimbursement_create_url = reverse('reimbursement-create')
        self.assertContains(response, 'href="{0}"'.format(reimbursement_create_url))

    def test_reverse_reimbursement_list_user_name_contains_link_to_reimbursement_update_name(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-list-user', kwargs={'username': 'carol'})
        response = self.client.get(url)
        reimbursement_update_url = reverse('reimbursement-update', kwargs={'pk': 1})
        self.assertContains(response, 'href="{0}"'.format(reimbursement_update_url))

@override_settings(MEDIA_ROOT='temp_documentation_files')
class ReimbursementUpdateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        reimbursement = Reimbursement.objects.create(
            user=user,
            submission_date=datetime.date.today())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('temp_documentation_files')
        super().tearDownClass()

    def test_reimbursements_number_update_url_maps_to_reimbursement_update_name(self):
        url = '/reimbursements/1/update/'
        reversed_name = reverse('reimbursement-update', kwargs={'pk': 1})
        self.assertEqual(url, reversed_name)

    def test_reverse_reimbursement_update_name_resolves_to_reimbursement_update_view(self):
        view = resolve(reverse('reimbursement-update', kwargs={'pk': 1}))
        self.assertEqual(view.func.view_class, ReimbursementUpdateView)

    def test_reverse_reimbursement_update_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('reimbursement-update', kwargs={'pk': 1})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_reimbursement_update_name_success_status_code_if_logged_in(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_reimbursement_update_name_redirects_to_current_page_after_logging_in(self):
        url = reverse('reimbursement-update', kwargs={'pk': 1})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)

    def test_reverse_reimbursement_update_name_contains_reimbursement_form(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-update', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, ReimbursementForm)

    def test_reimbursement_form_csrf(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_reverse_reimbursement_update_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'accounting/reimbursement_create.html')

    def test_reverse_reimbursement_update_name_not_found_status_code_if_logged_in_and_reimbursement_does_not_exist(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-update', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_reimbursement_update_name_not_found_status_code_if_logged_in_and_not_user_reimbursement(self):
        user_2 = CustomUser.objects.create_user(
            username='matt', password='Ilovemeatballs')
        reimbursement_2 = Reimbursement.objects.create(
            user=user_2,
            submission_date=datetime.date.today())
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-update', kwargs={'pk': reimbursement_2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_reimbursement_update_name_redirects_to_reimbursement_list_user_name_after_valid_post(self):
        test_file = SimpleUploadedFile('documentation.txt', b'Beer for $2.50.')
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('reimbursement-update', kwargs={'pk': 1})
        data = {
            'purchase_date': datetime.date.today(),
            'category': 'F/D',
            'description': 'Beer for a regular.',
            'amount': '2.50',
            'documentation': test_file,
        }
        response = self.client.post(url, data)
        success_url = reverse('reimbursement-list-user', kwargs={'username': 'carol'})
        self.assertRedirects(response, success_url)