from django.test import TestCase
from django.urls import reverse, resolve

from locations.forms import VenueForm
from locations.models import Region, State, City, Zip, Venue
from locations.views import VenueCreate

class VenueFormTests(TestCase):
    def setUp(self):
        region = Region.objects.create(name='ne')
        state = State.objects.create(name='New Jersey', region=region)
        city = City.objects.create(name='Jersey City', state=state)
        zip = Zip.objects.create(code='07302', city=city)
        Venue.objects.create(
            name='The Meatballery', address='4 Spaghetti Way',
            city=city, state=state, zip=zip)
        
    def test_venue_new_form_csrf(self):
        url = reverse('venue-create')
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')
        
    def test_venues_new_valid_post_data(self):
        url = reverse('venue-create')
        state = State.objects.get(name='New Jersey')
        data = {
            'name': 'Mama Bear Beer Bar',
            'address': '2 Kitten Mitten Plaza',
            'city': 'Furryville',
            'state': state,
            'zip': '07302',
        }
        response = self.client.post(url, data)
        self.assertEqual(Venue.objects.all().count(), 2)
        self.assertEqual(State.objects.all().count(), 1)
        self.assertEqual(City.objects.all().count(), 2)
        self.assertEqual(Zip.objects.all().count(), 2)
        
    def test_venues_new_invalid_post_data(self):
        url = reverse('venue-create')
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.errors)
        
    def test_venues_new_invalid_post_data_empty_fields(self):
        url = reverse('venue-create')
        data = {
            'name': '',
            'address': '',
            'city': '',
            'state': '',
            'zip': '',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Venue.objects.all().count(), 1)
        self.assertEqual(State.objects.all().count(), 1)
        self.assertEqual(City.objects.all().count(), 1)
        self.assertEqual(Zip.objects.all().count(), 1)

    def test_venues_update_form_csrf(self):
        url = reverse('venue-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')
        
    def test_venues_update_valid_post_data_name(self):
        url = reverse('venue-update', kwargs={'pk': 1})
        venue = Venue.objects.get(pk=1)
        data = {
            'name': 'Meatballs and Mead',
            'address': venue.address,
            'city': venue.city,
            'state': venue.state,
            'zip': venue.zip,
        }
        response = self.client.post(url, data)
        venue = Venue.objects.get(pk=1)
        venue_name = venue.name
        self.assertEqual(venue.name, 'Meatballs and Mead')
        self.assertEqual(Venue.objects.all().count(), 1)
        
    def test_venues_update_invalid_post_data(self):
        url = reverse('venue-update', kwargs={'pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.errors)
        
    def test_venues_update_invalid_post_data_empty_fields(self):
        url = reverse('venue-update', kwargs={'pk': 1})
        data = {
            'name': '',
            'address': '',
            'city': '',
            'state': '',
            'zip': '',
        }
        response = self.client.post(url, data)
        venue = Venue.objects.get(pk=1)
        venue_name = venue.name
        self.assertEqual(venue_name, 'The Meatballery')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Venue.objects.all().count(), 1)
        self.assertEqual(State.objects.all().count(), 1)
        self.assertEqual(City.objects.all().count(), 1)
        self.assertEqual(Zip.objects.all().count(), 1)

