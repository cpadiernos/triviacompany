from django.test import TestCase
from django.urls import reverse, resolve
from locations.models import Venue, Region, State, City, Zip
from locations.views import VenueListView, VenueCreate, VenueUpdate
from locations.forms import VenueForm

class VenueViewTests(TestCase):
    def setUp(self):
        region = Region.objects.create(name='ne')
        state = State.objects.create(name='New Jersey', region=region)
        city = City.objects.create(name='Jersey City', state=state)
        zip = Zip.objects.create(code='07302', city=city)
        Venue.objects.create(name='The Meatballery', city=city, state=state, zip=zip)

    def test_venues_view_success_status_code(self):
        url = reverse('venue-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_venues_url_resolves_venue_list_view(self):
        view = resolve('/venues/')
        self.assertEqual(view.func.view_class, VenueListView)
        
    def test_venues_new_view_success_status_code(self):
        url = reverse('venue-create')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_venues_new_url_resolves_venue_create(self):
        view = resolve('/venues/new/')
        self.assertEquals(view.func.view_class, VenueCreate)
        
    def test_venues_update_view_success_status_code(self):
        url = reverse('venue-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_venues_update_view_not_found_status_code(self):
        url = reverse('venue-update', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_venues_update_url_resolves_venue_update(self):
        view = resolve('/venues/1/update/')
        self.assertEqual(view.func.view_class, VenueUpdate)
        
    def test_venues_view_contains_link_to_venue_create(self):
        url = reverse('venue-list')
        create_url = reverse('venue-create')
        response = self.client.get(url)
        self.assertContains(response, 'href="{0}"'.format(create_url))
        
    def test_venues_view_contains_link_to_venue_update(self):
        url = reverse('venue-list')
        update_url = reverse('venue-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'href="{0}"'.format(update_url))

    def test_venues_new_contains_form(self):
        url = reverse('venue-create')
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, VenueForm)
        
    def test_venues_update_contains_form(self):
        url = reverse('venue-update', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, VenueForm)