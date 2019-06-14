import calendar
import datetime

from django.test import TestCase
from django.urls import reverse, resolve

from accounts.models import CustomUser
from locations.models import City, State, Zip, Venue
from schedule.filters import EventOccurrenceFilter
from schedule.forms import EventOccurrenceForm, ChangeHostForm
from schedule.models import Day, Time, Event, EventOccurrence
from schedule.views import (
    EventDetailView,
    EventOccurrenceListView,
    EventOccurrenceListViewHost,
    EventOccurrenceListViewPastHost,
    EventOccurrenceListViewFutureHost,
    EventOccurrenceListViewAvailable,
    EventOccurrenceUpdate,
    PickUp,
    RequestOff,
)

class EventDetailViewTests(TestCase):
    def setUp(self):
        host = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        venue = Venue.objects.create(name='The Meatballery')
        event = Event.objects.create(venue=venue)

    def test_events_number_url_maps_to_event_detail_name(self):
        url = '/events/1/'
        reversed_name = reverse('event-detail', kwargs={'pk': 1})
        self.assertEqual(url, reversed_name)
        
    def test_reverse_event_detail_name_resolves_to_event_detail_view(self):
        view = resolve(reverse('event-detail', kwargs={'pk': 1}))
        self.assertEqual(view.func.view_class, EventDetailView)
        
    def test_reverse_event_detail_name_success_status_code(self):
        url = reverse('event-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_reverse_event_detail_name_not_found_status_code(self):
        url = reverse('event-detail', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_event_detail_name_uses_correct_template(self):
        url = reverse('event-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'schedule/event_detail.html')
        
    # def test_reverse_event_detail_name_contains_link_to_update_event_detail_if_logged_in(self):
        # login = self.client.login(username='carol', password='Ilovespaghetti')
        # url = reverse('event-detail', kwargs={'pk': 1})
        # update_url = reverse('event-update', kwargs={'pk': 1})
        # response = self.client.get(url)
        # self.assertContains(response, 'href="{0}"'.format(update_url))
        
    # def test_reverse_event_detail_name_does_not_contain_link_to_update_event_detail_if_not_logged_in(self):
        # url = reverse('event-detail', kwargs={'pk': 1})
        # update_url = reverse('event-update', kwargs={'pk': 1})
        # response = self.client.get(url)
        # self.assertNotContains(response, 'href="{0}"'.format(update_url))

class EventOccurrenceListViewTests(TestCase):

    def test_events_url_maps_to_event_occurrence_list_name(self):
        url = '/events/'
        reversed_name = reverse('event-occurrence-list')
        self.assertEqual(url, reversed_name)
        
    def test_reverse_event_occurrence_list_name_resolves_to_event_occurrence_list_view(self):
        view = resolve(reverse('event-occurrence-list'))
        self.assertEqual(view.func.view_class, EventOccurrenceListView)
        
    def test_reverse_event_occurrence_list_name_success_status_code(self):
        url = reverse('event-occurrence-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_reverse_event_occurrence_list_name_uses_correct_template(self):
        url = reverse('event-occurrence-list')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'schedule/event_occurrence_list_with_filter.html')
        
    def test_reverse_event_occurrence_list_name_contains_event_occurrence_filter(self):
        url = reverse('event-occurrence-list')
        response = self.client.get(url)
        filter = response.context.get('filter')
        self.assertIsInstance(filter, EventOccurrenceFilter)
        
    def test_reverse_event_occurrence_list_name_contains_link_to_reverse_event_occurrence_list_name_aka_reset(self):
        url = reverse('event-occurrence-list')
        response = self.client.get(url)
        self.assertContains(response, 'href="{0}"'.format(url))
    
    def test_reverse_event_occurrence_list_name_shows_only_today_and_future_event_occurrences(self):
        day_before_today = datetime.date.today() - datetime.timedelta(days=1)
        today = datetime.date.today()
        day_after_today = datetime.date.today() + datetime.timedelta(days=1)

        venue = Venue.objects.create(name='The Meatballery')
        event = Event.objects.create(venue=venue)
        occurrence_past = EventOccurrence.objects.create(
            event=event, date=day_before_today)
        occurrence_today = EventOccurrence.objects.create(
            event=event, date=today)
        occurrence_future = EventOccurrence.objects.create(
            event=event, date=day_after_today)
            
        url = reverse('event-occurrence-list')
        response = self.client.get(url)
        self.assertContains(response, 'The Meatballery')
        # leading spaces in case test is done at beginning of the month (for months after months with 31 days)
        # i.e. " 1, 2019" should pass, but " 31,2019" should not.
        self.assertContains(response, f' {day_after_today.day}, {day_after_today.year}')
        self.assertContains(response, f' {today.day}, {today.year}')
        self.assertNotContains(response, f' {day_before_today.day}, {day_before_today.year}')
    
    def test_reverse_event_occurrence_list_name_contains_link_to_event_detail_name(self):
        venue = Venue.objects.create(name='The Meatballery')
        event = Event.objects.create(venue=venue)
        occurrence = EventOccurrence.objects.create(
            event=event, date=datetime.date.today())
        
        url = reverse('event-occurrence-list')
        response = self.client.get(url)
        event_detail_url = reverse('event-detail', kwargs={'pk': 1})
        self.assertContains(response, 'href="{0}"'.format(event_detail_url))
        
class EventOccurrenceListHostViewTests(TestCase):
    def setUp(self):
        host = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
            
    def test_events_username_all_url_maps_to_event_occurrence_list_host_name(self):
        url = '/events/carol/all/'
        reversed_name = reverse('event-occurrence-list-host', kwargs={'username': 'carol'})
        self.assertEqual(url, reversed_name)

    def test_reverse_event_occurrence_list_host_name_resolves_to_event_occurrence_list_view_host_view(self):
        view = resolve(reverse('event-occurrence-list-host', kwargs={'username': 'carol'}))
        self.assertEqual(view.func.view_class, EventOccurrenceListViewHost)
        
    def test_reverse_event_occurrence_list_host_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-host', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'schedule/event_occurrence_list.html')
        
    def test_reverse_event_occurrence_list_host_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('event-occurrence-list-host', kwargs={'username': 'carol'})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))
        
    def test_reverse_event_occurrence_list_host_name_success_status_code_if_logged_in(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-host', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_reverse_event_occurrence_list_host_name_redirects_to_current_page_after_logging_in(self):
        url = reverse('event-occurrence-list-host', kwargs={'username': 'carol'})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)
        
    def test_reverse_event_occurrence_list_host_name_not_found_status_code_if_not_correct_host(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-host', kwargs={'username': 'matt'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_event_occurrence_list_host_includes_only_logged_in_host_event_occurrences(self):
        host = CustomUser.objects.get(username='carol')
        venue = Venue.objects.create(name='The Meatballery')
        event = Event.objects.create(venue=venue)
        occurrence = EventOccurrence.objects.create(
            event=event, host=host)
        
        host_2 = CustomUser.objects.create_user(
            username='matt', password='Iloveanimals')
        venue_2 = Venue.objects.create(name='Pet Shop')
        event_2 = Event.objects.create(venue=venue_2)
        occurrence_2 = EventOccurrence.objects.create(
            event=event_2, host=host_2)
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-host', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertContains(response, 'The Meatballery')
        self.assertNotContains(response, 'Pet Shop')
        
    def test_reverse_event_occurrence_list_host_name_contains_link_to_event_detail_name(self):
        host = CustomUser.objects.get(username='carol')
        venue = Venue.objects.create(name='The Meatballery')
        event = Event.objects.create(venue=venue)
        occurrence = EventOccurrence.objects.create(
            event=event, host=host)
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-host', kwargs={'username': 'carol'})
        response = self.client.get(url)
        event_detail_url = reverse('event-detail', kwargs={'pk': 1})
        self.assertContains(response, 'href="{0}"'.format(event_detail_url))

class EventOccurrenceListPastHostViewTests(TestCase):
    def setUp(self):
        host = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
            
    def test_events_username_past_url_maps_to_event_occurrence_list_past_host_name(self):
        url = '/events/carol/past/'
        reversed_name = reverse('event-occurrence-list-past-host', kwargs={'username': 'carol'})
        self.assertEqual(url, reversed_name)
        
    def test_reverse_event_occurrence_list_past_host_name_resolves_to_event_occurrence_list_view_past_host_view(self):
        view = resolve(reverse('event-occurrence-list-past-host', kwargs={'username': 'carol'}))
        self.assertEqual(view.func.view_class, EventOccurrenceListViewPastHost)
        
    def test_reverse_event_occurrence_list_past_host_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-past-host', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'schedule/event_occurrence_list.html')
        
    def test_reverse_event_occurrence_list_past_host_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('event-occurrence-list-past-host', kwargs={'username': 'carol'})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))
        
    def test_reverse_event_occurrence_list_past_host_name_success_status_code_if_logged_in(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-past-host', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_reverse_event_occurrence_list_past_host_name_redirects_to_current_page_after_logging_in(self):
        url = reverse('event-occurrence-list-past-host', kwargs={'username': 'carol'})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)
        
    def test_reverse_event_occurrence_list_past_host_name_not_found_status_code_if_not_correct_host(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-past-host', kwargs={'username': 'matt'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_event_occurrence_list_past_host_includes_only_logged_in_host_event_occurrences_today_and_in_past(self):
        day_before_today = datetime.date.today() - datetime.timedelta(days=1)
        today = datetime.date.today()
        day_after_today = datetime.date.today() + datetime.timedelta(days=1)

        host = CustomUser.objects.get(username='carol')
        venue = Venue.objects.create(name='The Meatballery')
        event = Event.objects.create(venue=venue)
        occurrence_past = EventOccurrence.objects.create(
            event=event, host=host, date=day_before_today)
        occurrence_today = EventOccurrence.objects.create(
            event=event, host=host, date=today)
        occurrence_future = EventOccurrence.objects.create(
            event=event, host=host, date=day_after_today)
        
        host_2 = CustomUser.objects.create_user(
            username='matt', password='Iloveanimals')
        venue_2 = Venue.objects.create(name='Pet Shop')
        event_2 = Event.objects.create(venue=venue_2)
        occurrence_2 = EventOccurrence.objects.create(
            event=event_2, host=host_2)
            
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-past-host', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertContains(response, 'The Meatballery')
        self.assertNotContains(response, 'Pet Shop')
        # leading spaces in case test is done at end of the month (for months with 31 days)
        # i.e. " 31,2019" should pass, but " 1, 2019" should not.
        self.assertContains(response, f' {day_before_today.day}, {day_before_today.year}')
        self.assertContains(response, f' {today.day}, {today.year}')
        self.assertNotContains(response, f' {day_after_today.day}, {day_after_today.year}')
        
    def test_reverse_event_occurrence_list_past_host_name_contains_link_to_event_detail_name(self):
        host = CustomUser.objects.get(username='carol')
        venue = Venue.objects.create(name='The Meatballery')
        event = Event.objects.create(venue=venue)
        occurrence = EventOccurrence.objects.create(
            event=event, host=host, date=datetime.date.today())
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-past-host', kwargs={'username': 'carol'})
        response = self.client.get(url)
        event_detail_url = reverse('event-detail', kwargs={'pk': 1})
        self.assertContains(response, 'href="{0}"'.format(event_detail_url))
        
class EventOccurrenceListFutureHostViewTests(TestCase):
    def setUp(self):
        host = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
            
    def test_events_username_future_url_maps_to_event_occurrence_list_future_host_name(self):
        url = '/events/carol/future/'
        reversed_name = reverse('event-occurrence-list-future-host', kwargs={'username': 'carol'})
        self.assertEqual(url, reversed_name)
        
    def test_reverse_event_occurrence_list_future_host_name_resolves_to_event_occurrence_list_view_future_host_view(self):
        view = resolve(reverse('event-occurrence-list-future-host', kwargs={'username': 'carol'}))
        self.assertEqual(view.func.view_class, EventOccurrenceListViewFutureHost)
        
    def test_reverse_event_occurrence_list_future_host_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-future-host', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'schedule/event_occurrence_list.html')

    def test_reverse_event_occurrence_list_future_host_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('event-occurrence-list-future-host', kwargs={'username': 'carol'})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))
        
    def test_reverse_event_occurrence_list_future_host_name_success_status_code_if_logged_in(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-future-host', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_reverse_event_occurrence_list_future_host_name_redirects_to_current_page_after_logging_in(self):
        url = reverse('event-occurrence-list-future-host', kwargs={'username': 'carol'})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)
        
    def test_reverse_event_occurrence_list_future_host_name_not_found_status_code_if_not_correct_host(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-future-host', kwargs={'username': 'matt'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_event_occurrence_list_future_host_includes_only_logged_in_host_event_occurrences_today_and_in_future(self):
        day_before_today = datetime.date.today() - datetime.timedelta(days=1)
        today = datetime.date.today()
        day_after_today = datetime.date.today() + datetime.timedelta(days=1)

        host = CustomUser.objects.get(username='carol')
        venue = Venue.objects.create(name='The Meatballery')
        event = Event.objects.create(venue=venue)
        occurrence_past = EventOccurrence.objects.create(
            event=event, host=host, date=day_before_today)
        occurrence_today = EventOccurrence.objects.create(
            event=event, host=host, date=today)
        occurrence_future = EventOccurrence.objects.create(
            event=event, host=host, date=day_after_today)
        
        host_2 = CustomUser.objects.create_user(
            username='matt', password='Iloveanimals')
        venue_2 = Venue.objects.create(name='Pet Shop')
        event_2 = Event.objects.create(venue=venue_2)
        occurrence_2 = EventOccurrence.objects.create(
            event=event_2, host=host_2)
            
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-future-host', kwargs={'username': 'carol'})
        response = self.client.get(url)
        self.assertContains(response, 'The Meatballery')
        self.assertNotContains(response, 'Pet Shop')
        # leading spaces in case test is done at beginning of the month (for months after months with 31 days)
        # i.e. " 1, 2019" should pass, but " 31,2019" should not.
        self.assertNotContains(response, f' {day_before_today.day}, {day_before_today.year}')
        self.assertContains(response, f' {today.day}, {today.year}')
        self.assertContains(response, f' {day_after_today.day}, {day_after_today.year}')
        
    def test_reverse_event_occurrence_list_future_host_name_contains_link_to_event_detail_name(self):
        host = CustomUser.objects.get(username='carol')
        venue = Venue.objects.create(name='The Meatballery')
        event = Event.objects.create(venue=venue)
        occurrence = EventOccurrence.objects.create(
            event=event, host=host, date=datetime.date.today())
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-future-host', kwargs={'username': 'carol'})
        response = self.client.get(url)
        event_detail_url = reverse('event-detail', kwargs={'pk': 1})
        self.assertContains(response, 'href="{0}"'.format(event_detail_url))

class EventOccurrenceListAvailableViewTests(TestCase):
    def setUp(self):
        host = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')

    def test_events_available_url_maps_to_event_occurrence_list_availabe_name(self):
        url = '/events/available/'
        reversed_name = reverse('event-occurrence-list-available')
        self.assertEqual(url, reversed_name)

    def test_reverse_event_occurrence_list_available_name_resolves_to_event_occurrence_list_view_available_view(self):
        view = resolve(reverse('event-occurrence-list-available'))
        self.assertEqual(view.func.view_class, EventOccurrenceListViewAvailable)
        
    def test_reverse_event_occurrence_list_available_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-available')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'schedule/event_occurrence_list.html')
        
    def test_reverse_event_occurrence_list_available_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('event-occurrence-list-available')
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))
        
    def test_reverse_event_occurrence_list_available_name_success_status_code_if_logged_in(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-available')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_reverse_event_occurrence_list_available_name_redirects_to_current_page_after_logging_in(self):
        url = reverse('event-occurrence-list-available')
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)

    def test_reverse_event_occurrence_list_available_includes_all_available_event_occurrences_today_and_in_future(self):
        day_before_today = datetime.date.today() - datetime.timedelta(days=1)
        today = datetime.date.today()
        day_after_today = datetime.date.today() + datetime.timedelta(days=1)

        host = CustomUser.objects.get(username='carol')
        venue = Venue.objects.create(name='The Meatballery')
        event = Event.objects.create(venue=venue)
        occurrence_past = EventOccurrence.objects.create(
            event=event, host=host, date=day_before_today,
            change_host=True)
        occurrence_today = EventOccurrence.objects.create(
            event=event, host=host, date=today,
            change_host=True)
        occurrence_future = EventOccurrence.objects.create(
            event=event, host=host, date=day_after_today,
            change_host=True)
        
        host_2 = CustomUser.objects.create_user(
            username='matt', password='Iloveanimals')
        venue_2 = Venue.objects.create(name='Pet Shop')
        event_2 = Event.objects.create(venue=venue_2)
        occurrence_past_2 = EventOccurrence.objects.create(
            event=event_2, host=host_2, date=day_before_today,
            change_host=True)
        occurrence_today_2 = EventOccurrence.objects.create(
            event=event_2, host=host_2, date=today,
            change_host=True)
        occurrence_future_2 = EventOccurrence.objects.create(
            event=event_2, host=host_2, date=day_after_today,
            change_host=True)
            
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-available')
        response = self.client.get(url)
        self.assertContains(response, 'The Meatballery', count=2)
        self.assertContains(response, 'Pet Shop', count=2)
        # leading spaces in case test is done at beginning of the month (for months after months with 31 days)
        # i.e. " 1, 2019" should pass, but " 31,2019" should not.
        self.assertNotContains(response, f' {day_before_today.day}, {day_before_today.year}')
        self.assertContains(response, f' {today.day}, {today.year}', count=2)
        self.assertContains(response, f' {day_after_today.day}, {day_after_today.year}', count=2)
        
    def test_reverse_event_occurrence_list_available_name_contains_link_to_event_detail_name(self):
        host = CustomUser.objects.get(username='carol')
        venue = Venue.objects.create(name='The Meatballery')
        event = Event.objects.create(venue=venue)
        occurrence = EventOccurrence.objects.create(
            event=event, host=host, date=datetime.date.today(),
            change_host=True)
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-list-available')
        response = self.client.get(url)
        event_detail_url = reverse('event-detail', kwargs={'pk': 1})
        self.assertContains(response, 'href="{0}"'.format(event_detail_url))
        
class EventOccurrenceUpdateViewTests(TestCase):
    def setUp(self):
        today = datetime.date.today()
        today_int = today.weekday()
        day = Day.objects.create(day=today_int)
        
        host = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
            
        venue = Venue.objects.create(name='The Meatballery')
        event = Event.objects.create(venue=venue)
        occurrence = EventOccurrence.objects.create(
            host=host,
            event=event,
            day=day,
            date=today)
            
    def test_events_number_update_url_maps_to_event_occurrence_update_name(self):
        url = '/events/1/update/'
        reversed_name = reverse('event-occurrence-update', kwargs={'pk': 1})
        self.assertEqual(url, reversed_name)
        
    def test_reverse_event_occurrence_update_name_resolves_to_event_occurrence_update_view(self):
        view = resolve(reverse('event-occurrence-update', kwargs={'pk': 1}))
        self.assertEqual(view.func.view_class, EventOccurrenceUpdate)
        
    def test_reverse_event_occurrence_update_name_uses_correct_template(self):
        second_before_now = (datetime.datetime.now() - datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_before_now)
        
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'schedule/event_occurrence_form.html')
        
    def test_reverse_event_occurrence_update_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('event-occurrence-update', kwargs={'pk': 1})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))
        
    def test_reverse_event_occurrence_update_name_success_status_code_if_logged_in_and_is_user_event_occurrence_passed(self):
        second_before_now = (datetime.datetime.now() - datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_before_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_reverse_event_occurrence_update_name_not_found_status_code_if_logged_in_and_is_user_event_occurrence_future(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
            
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_event_occurrence_update_name_not_found_status_code_if_logged_in_and_not_user_event_occurrence(self):
        second_before_now = (datetime.datetime.now() - datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_before_now)

        host_2 = CustomUser.objects.create_user(
            username='matt', password='Iloveanimals')
            
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.host = host_2
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_event_occurrence_update_name_not_found_status_code_if_logged_in_and_event_occurrence_passed_and_cancelled_ahead(self):
        second_before_now = (datetime.datetime.now() - datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_before_now)
        
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.cancelled_ahead = True
        occurrence.save()
            
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_event_occurrence_update_name_not_found_status_code_if_logged_in_and_event_occurrence_future_and_cancelled_ahead(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)
        
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.cancelled_ahead = True
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_event_occurrence_update_name_not_found_status_code_if_logged_in_and_event_occurrence_does_not_exist(self):
        second_before_now = (datetime.datetime.now() - datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_before_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-update', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_event_occurrence_update_name_redirects_to_current_page_after_logging_in(self):
        second_before_now = (datetime.datetime.now() - datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_before_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
            
        url = reverse('event-occurrence-update', kwargs={'pk': 1})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)
        
    def test_reverse_event_occurrence_update_name_contains_event_occurrence_update_form(self):
        second_before_now = (datetime.datetime.now() - datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_before_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-update', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, EventOccurrenceForm)
        
    def test_reverse_event_occurrence_update_name_redirects_to_event_occurrence_list_host_name_after_valid_post(self):
        two_hours_before_now = (datetime.datetime.now() - datetime.timedelta(hours=2)).time()
        time = Time.objects.create(time=two_hours_before_now)
        
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-update', kwargs={'pk': 1})
        data = {
            'status': 'No Game',
            'cancellation_reason': 'Holiday',
        }
        response = self.client.post(url, data)
        success_url = reverse('event-occurrence-list-host', kwargs={'username': 'carol'})
        self.assertRedirects(response, success_url)
        
    def test_event_occurrence_form_csrf(self):
        second_before_now = (datetime.datetime.now() - datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_before_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('event-occurrence-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

class RequestOffViewTests(TestCase):
    def setUp(self):
        today = datetime.date.today()
        today_int = today.weekday()
        day = Day.objects.create(day=today_int)
        
        host = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
            
        venue = Venue.objects.create(name='The Meatballery')
        event = Event.objects.create(venue=venue)
        occurrence = EventOccurrence.objects.create(
            host=host,
            event=event,
            day=day,
            date=today,
            change_host=False)
            
    def test_events_number_request_off_url_maps_to_request_off_name(self):
        url = '/events/1/request-off/'
        reversed_name = reverse('request-off', kwargs={'pk': 1})
        self.assertEqual(url, reversed_name)
        
    def test_reverse_request_off_name_resolves_to_request_off_view(self):
        view = resolve(reverse('request-off', kwargs={'pk': 1}))
        self.assertEqual(view.func.view_class, RequestOff)
        
    def test_reverse_request_off_name_uses_correct_template(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)
        
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('request-off', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'schedule/change_host_form.html')
        
    def test_reverse_request_off_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('request-off', kwargs={'pk': 1})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))
        
    def test_reverse_request_off_name_success_status_code_if_logged_in_and_is_user_event_occurrence_future(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('request-off', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_reverse_request_off_name_not_found_status_code_if_logged_in_and_is_user_event_occurrence_passed(self):
        second_before_now = (datetime.datetime.now() - datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_before_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
            
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('request-off', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_request_off_name_not_found_status_code_if_logged_in_and_not_user_event_occurrence(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)

        host_2 = CustomUser.objects.create_user(
            username='matt', password='Iloveanimals')
            
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.host = host_2
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('request-off', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_request_off_name_not_found_status_code_if_logged_in_and_event_occurrence_passed_and_cancelled_ahead(self):
        second_before_now = (datetime.datetime.now() - datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_before_now)
        
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.cancelled_ahead = True
        occurrence.save()
            
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('request-off', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_request_off_name_not_found_status_code_if_logged_in_and_event_occurrence_future_and_cancelled_ahead(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)
        
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.cancelled_ahead = True
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('request-off', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_request_off_name_not_found_status_code_if_logged_in_and_event_occurrence_future_and_change_host_true(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)
        
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.change_host = True
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('request-off', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_request_off_not_found_status_code_if_logged_in_and_event_occurrence_does_not_exist(self):
        second_before_now = (datetime.datetime.now() - datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_before_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('request-off', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_request_off_name_redirects_to_current_page_after_logging_in(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
            
        url = reverse('request-off', kwargs={'pk': 1})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)
        
    def test_reverse_request_off_name_contains_change_host_form(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('request-off', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, ChangeHostForm)
        
    def test_reverse_request_off_name_contains_request_off_content(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('request-off', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'Request Day Off?')
        self.assertContains(response, 'request off for')
        self.assertContains(response, 'value="{0}"'.format('Yes, Request Off'))
        
    def test_reverse_request_off_name_updates_change_host_after_confirmation(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('request-off', kwargs={'pk': 1})
        data = {}
        response = self.client.post(url, data)
        occurrence.refresh_from_db()
        self.assertIs(occurrence.change_host, True)
        
    def test_reverse_request_off_name_redirects_to_event_occurrence_list_host_name_with_message_after_valid_post(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)
        
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('request-off', kwargs={'pk': 1})
        data = {}
        response = self.client.post(url, data, follow=True)
        self.assertContains(response, 'Success! You requested a day off.')
        
    def test_reverse_request_off_name_redirects_to_event_occurrence_list_host_name_after_valid_post(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)
        
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('request-off', kwargs={'pk': 1})
        data = {}
        response = self.client.post(url, data)
        success_url = reverse('event-occurrence-list-host', kwargs={'username': 'carol'})
        self.assertRedirects(response, success_url)
        
    def test_change_host_form_csrf(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('request-off', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

class PickUpViewTests(TestCase):
    def setUp(self):
        today = datetime.date.today()
        today_int = today.weekday()
        day = Day.objects.create(day=today_int)
        
        host = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
            
        venue = Venue.objects.create(name='The Meatballery')
        event = Event.objects.create(venue=venue)
        occurrence = EventOccurrence.objects.create(
            host=host,
            event=event,
            day=day,
            date=today,
            change_host=True)
            
    def test_events_number_pick_up_url_maps_to_pick_up_name(self):
        url = '/events/1/pick-up/'
        reversed_name = reverse('pick-up', kwargs={'pk': 1})
        self.assertEqual(url, reversed_name)
        
    def test_reverse_pick_up_name_resolves_to_pick_up_view(self):
        view = resolve(reverse('pick-up', kwargs={'pk': 1}))
        self.assertEqual(view.func.view_class, PickUp)
        
    def test_reverse_pick_up__name_uses_correct_template(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)
        
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pick-up', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'schedule/change_host_form.html')
        
    def test_reverse_pick_up_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('pick-up', kwargs={'pk': 1})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))
        
    def test_reverse_pick_up_name_success_status_code_if_logged_in_and_is_user_event_occurrence_future(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pick-up', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_reverse_pick_up_name_not_found_status_code_if_logged_in_and_is_user_event_occurrence_passed(self):
        second_before_now = (datetime.datetime.now() - datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_before_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
            
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pick-up', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_pick_up_name_not_found_status_code_if_logged_in_and_event_occurrence_passed_and_cancelled_ahead(self):
        second_before_now = (datetime.datetime.now() - datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_before_now)
        
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.cancelled_ahead = True
        occurrence.save()
            
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pick-up', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_pick_up_name_not_found_status_code_if_logged_in_and_event_occurrence_future_and_cancelled_ahead(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)
        
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.cancelled_ahead = True
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pick-up', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_pick_up_name_not_found_status_code_if_logged_in_and_event_occurrence_future_and_change_host_false(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)
        
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.change_host = False
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pick-up', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_pick_up_not_found_status_code_if_logged_in_and_event_occurrence_does_not_exist(self):
        second_before_now = (datetime.datetime.now() - datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_before_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pick-up', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_reverse_pick_up_name_redirects_to_current_page_after_logging_in(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
            
        url = reverse('pick-up', kwargs={'pk': 1})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)
        
    def test_reverse_pick_up_name_contains_change_host_form(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pick-up', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, ChangeHostForm)
        
    def test_reverse_pick_up_name_contains_pick_up_content(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pick-up', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'Pick Up Shift?')
        self.assertContains(response, 'pick up')
        self.assertContains(response, 'value="{0}"'.format('Yes, Pick Up'))
        
    def test_reverse_pick_up_name_updates_change_host_after_confirmation(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()

        host_2 = CustomUser.objects.create_user(
            username='matt', password='Iloveanimals')
            
        login = self.client.login(username='matt', password='Iloveanimals')
        url = reverse('pick-up', kwargs={'pk': 1})
        data = {}
        response = self.client.post(url, data)
        occurrence.refresh_from_db()
        self.assertIs(occurrence.change_host, False)
        
    def test_reverse_pick_up_name_updates_host_after_confirmation(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        host_2 = CustomUser.objects.create_user(
            username='matt', password='Iloveanimals')
            
        login = self.client.login(username='matt', password='Iloveanimals')
        url = reverse('pick-up', kwargs={'pk': 1})
        data = {}
        response = self.client.post(url, data)
        occurrence.refresh_from_db()
        self.assertEqual(str(occurrence.host), 'matt')

    def test_reverse_pick_up_name_redirects_to_event_occurrence_list_host_name_with_message_after_valid_post(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)
        
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pick-up', kwargs={'pk': 1})
        data = {}
        response = self.client.post(url, data, follow=True)
        self.assertContains(response, 'Thanks for picking up the shift!')
        
    def test_reverse_pick_up_name_redirects_to_event_occurrence_list_host_name_after_valid_post(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)
        
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pick-up', kwargs={'pk': 1})
        data = {}
        response = self.client.post(url, data)
        success_url = reverse('event-occurrence-list-host', kwargs={'username': 'carol'})
        self.assertRedirects(response, success_url)
        
    def test_change_host_form_csrf(self):
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)

        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.time = time
        occurrence.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('pick-up', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')