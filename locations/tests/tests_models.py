from django.db import IntegrityError
from django.test import TestCase
from accounts.models import CustomUser
from locations.models import Region, State, City, Zip, Venue, ManagementPeriod

class RegionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Region.objects.create(name='ne')

    def test_name_label(self):
        region = Region.objects.get(name='ne')
        field_label = region._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')
        
    def test_name_max_length(self):
        region = Region.objects.get(name='ne')
        max_length = region._meta.get_field('name').max_length
        self.assertEqual(max_length, 10)

    def test_pk(self):
        region = Region.objects.get(name='ne')
        self.assertEqual(region.pk, region.name)
        
    def test_string_representation(self):
        region = Region.objects.get(name='ne')
        self.assertEqual(str(region), region.name)
        
    def test_clean(self):
        region = Region.objects.get(name='ne')
        region.clean()
        self.assertEqual(region.name, 'NE')

class StateModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        region = Region.objects.create(name='NE')
        State.objects.create(name='New Jersey', region=region)

    def test_name_label(self):
        state = State.objects.get(name='New Jersey')
        field_label = state._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_pk(self):
        state = State.objects.get(name='New Jersey')
        self.assertEqual(state.pk, state.name)

    def test_region_label(self):
        state = State.objects.get(name='New Jersey')
        field_label = state._meta.get_field('region').verbose_name
        self.assertEqual(field_label, 'region')

    def test_region_delete_set_null(self):
        region = Region.objects.get(name='NE')
        region.delete()
        state = State.objects.get(name='New Jersey')
        count = State.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(state.region, None)
        
    def test_region_related_name(self):
        state = State.objects.get(name='New Jersey')
        related_name = state.region._meta.get_field('states').related_name
        self.assertEqual(related_name, 'states')

    def test_string_representation(self):
        state = State.objects.get(name='New Jersey')
        self.assertEqual(str(state), state.name)

class CityModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        region = Region.objects.create(name='s')
        state = State.objects.create(name='New Jersey', region=region)
        City.objects.create(name='Jersey City', state=state)

    def test_name_label(self):
        city = City.objects.get(name='Jersey City')
        field_label = city._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')
        
    def test_name_max_length(self):
        city = City.objects.get(name='Jersey City')
        max_length = city._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)

    def test_state_label(self):
        city = City.objects.get(name='Jersey City')
        field_label = city._meta.get_field('state').verbose_name
        self.assertEqual(field_label, 'state')
        
    def test_state_delete_set_null(self):
        state = State.objects.get(name='New Jersey')
        state.delete()
        city = City.objects.get(name='Jersey City')
        count = City.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(city.state, None)
        
    def test_state_related_name(self):
        city = City.objects.get(name='Jersey City')
        related_name = city.state._meta.get_field('cities').related_name
        self.assertEqual(related_name, 'cities')

    def test_verbose_name_plural(self):
        plural_name = City._meta.verbose_name_plural
        self.assertEqual(plural_name, 'cities')

    def test_city_and_state_unique_together(self):
        state = State.objects.get(name='New Jersey')
        with self.assertRaises(IntegrityError):
            City.objects.create(name='Jersey City', state=state)

    def test_string_representation(self):
        city = City.objects.get(name='Jersey City')
        self.assertEqual(str(city), '{0}, {1}'.format(city.name, city.state))

class ZipModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        region = Region.objects.create(name='ne')
        state = State.objects.create(name='New Jersey', region=region)
        city = City.objects.create(name='Jersey City', state=state)
        Zip.objects.create(code='07302', city=city)

    def test_code_label(self):
        zip = Zip.objects.get(code='07302')
        field_label = zip._meta.get_field('code').verbose_name
        self.assertEqual(field_label, 'code')

    def test_city_label(self):
        zip = Zip.objects.get(code='07302')
        field_label = zip._meta.get_field('city').verbose_name
        self.assertEqual(field_label, 'city')
        
    def test_city_delete_set_null(self):
        city = City.objects.get(name='Jersey City')
        city.delete()
        zip = Zip.objects.get(code='07302')
        count = Zip.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(zip.city, None)
        
    def test_city_related_name(self):
        zip = Zip.objects.get(code='07302')
        related_name = zip.city._meta.get_field('zips').related_name
        self.assertEqual(related_name, 'zips')

    def test_zip_and_city_unique_together(self):
        city = City.objects.get(name='Jersey City')
        with self.assertRaises(IntegrityError):
            Zip.objects.create(code='07302', city=city)

    def test_string_representation(self):
        zip = Zip.objects.get(code='07302')
        self.assertEqual(str(zip), zip.code)

class VenueModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        region = Region.objects.create(name='ne')
        state = State.objects.create(name='New Jersey', region=region)
        city = City.objects.create(name='Jersey City', state=state)
        zip = Zip.objects.create(code='07302', city=city)
        Venue.objects.create(name='The Meatballery', city=city, state=state, zip=zip)
        
    def test_name_label(self):
        venue = Venue.objects.get(id=1)
        field_label = venue._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')
        
    def test_name_label(self):
        venue = Venue.objects.get(id=1)
        field_label = venue._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')
        
    def test_name_max_length(self):
        venue = Venue.objects.get(id=1)
        max_length = venue._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)
        
    def test_address_label(self):
        venue = Venue.objects.get(id=1)
        field_label = venue._meta.get_field('address').verbose_name
        self.assertEqual(field_label, 'address')
        
    def test_address_max_length(self):
        venue = Venue.objects.get(id=1)
        max_length = venue._meta.get_field('address').max_length
        self.assertEqual(max_length, 200)
        
    def test_additional_address_label(self):
        venue = Venue.objects.get(id=1)
        field_label = venue._meta.get_field('additional_address').verbose_name
        self.assertEqual(field_label, 'additional address')
        
    def test_additional_address_max_length(self):
        venue = Venue.objects.get(id=1)
        max_length = venue._meta.get_field('additional_address').max_length
        self.assertEqual(max_length, 200)
        
    def test_city_label(self):
        venue = Venue.objects.get(id=1)
        field_label = venue._meta.get_field('city').verbose_name
        self.assertEqual(field_label, 'city')
        
    def test_city_delete_set_null(self):
        city = City.objects.get(name='Jersey City')
        city.delete()
        venue = Venue.objects.get(id=1)
        count = Venue.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(venue.city, None)
        
    def test_city_related_name(self):
        venue = Venue.objects.get(id=1)
        related_name = venue.city._meta.get_field('venues').related_name
        self.assertEqual(related_name, 'venues')
        
    def test_state_label(self):
        venue = Venue.objects.get(id=1)
        field_label = venue._meta.get_field('state').verbose_name
        self.assertEqual(field_label, 'state')
        
    def test_state_delete_set_null(self):
        state = State.objects.get(name='New Jersey')
        state.delete()
        venue = Venue.objects.get(id=1)
        count = Venue.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(venue.state, None)
        
    def test_state_related_name(self):
        venue = Venue.objects.get(id=1)
        related_name = venue.state._meta.get_field('venues').related_name
        self.assertEqual(related_name, 'venues')
        
    def test_zip_label(self):
        venue = Venue.objects.get(id=1)
        field_label = venue._meta.get_field('zip').verbose_name
        self.assertEqual(field_label, 'zip')
        
    def test_zip_delete_set_null(self):
        zip = Zip.objects.get(code='07302')
        zip.delete()
        venue = Venue.objects.get(id=1)
        count = Venue.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(venue.zip, None)
        
    def test_zip_related_name(self):
        venue = Venue.objects.get(id=1)
        related_name = venue.zip._meta.get_field('venues').related_name
        self.assertEqual(related_name, 'venues')
        
    def test_email_label(self):
        venue = Venue.objects.get(id=1)
        field_label = venue._meta.get_field('email').verbose_name
        self.assertEqual(field_label, 'email')
        
    def test_email_max_length(self):
        venue = Venue.objects.get(id=1)
        max_length = venue._meta.get_field('email').max_length
        self.assertEqual(max_length, 200)
        
    def test_phone_number_label(self):
        venue = Venue.objects.get(id=1)
        field_label = venue._meta.get_field('phone_number').verbose_name
        self.assertEqual(field_label, 'phone number')
        
    def test_website_label(self):
        venue = Venue.objects.get(id=1)
        field_label = venue._meta.get_field('website').verbose_name
        self.assertEqual(field_label, 'website')
        
    def test_website_max_length(self):
        venue = Venue.objects.get(id=1)
        max_length = venue._meta.get_field('website').max_length
        self.assertEqual(max_length, 200)
        
    def test_av_setup_label(self):
        venue = Venue.objects.get(id=1)
        field_label = venue._meta.get_field('av_setup').verbose_name
        self.assertEqual(field_label, 'av setup')
        
    def test_managers_label(self):
        venue = Venue.objects.get(id=1)
        field_label = venue._meta.get_field('managers').verbose_name
        self.assertEqual(field_label, 'managers')
        
    def test_string_representation(self):
        venue = Venue.objects.get(id=1)
        self.assertEqual(str(venue), venue.name)
        
    # def test_display_manager(self):
    
class ManagementPeriodModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        manager = CustomUser.objects.create_user(username='carol', password='Ilovespaghetti')
        region = Region.objects.create(name='ne')
        state = State.objects.create(name='New Jersey', region=region)
        city = City.objects.create(name='Jersey City', state=state)
        zip = Zip.objects.create(code='07302', city=city)
        venue = Venue.objects.create(name='The Meatballery', city=city, state=state, zip=zip)
        ManagementPeriod.objects.create(venue=venue, manager=manager)
        
    def test_venue_label(self):
        management_period = ManagementPeriod.objects.get(id=1)
        field_label = management_period._meta.get_field('venue').verbose_name
        self.assertEqual(field_label, 'venue')

    def test_venue_delete_set_null(self):
        venue = Venue.objects.get(id=1)
        venue.delete()
        management_period = ManagementPeriod.objects.get(id=1)
        count = ManagementPeriod.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(management_period.venue, None)
        
    def test_venue_related_name(self):
        management_period = ManagementPeriod.objects.get(id=1)
        related_name = management_period.venue._meta.get_field('management_periods').related_name
        self.assertEqual(related_name, 'management_periods')
    
    def test_manager_label(self):
        management_period = ManagementPeriod.objects.get(id=1)
        field_label = management_period._meta.get_field('manager').verbose_name
        self.assertEqual(field_label, 'manager')
        
    def test_manager_delete_set_null(self):
        manager = CustomUser.objects.get(id=1)
        manager.delete()
        management_period = ManagementPeriod.objects.get(id=1)
        count = ManagementPeriod.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(management_period.manager, None)
        
    def test_manager_related_name(self):
        management_period = ManagementPeriod.objects.get(id=1)
        related_name = management_period.manager._meta.get_field('management_periods').related_name
        self.assertEqual(related_name, 'management_periods')
        
    def test_date_started_label(self):
        management_period = ManagementPeriod.objects.get(id=1)
        field_label = management_period._meta.get_field('date_started').verbose_name
        self.assertEqual(field_label, 'date started')
        
    def test_date_ended_label(self):
        management_period = ManagementPeriod.objects.get(id=1)
        field_label = management_period._meta.get_field('date_ended').verbose_name
        self.assertEqual(field_label, 'date ended')
        
    def test_notes_label(self):
        management_period = ManagementPeriod.objects.get(id=1)
        field_label = management_period._meta.get_field('notes').verbose_name
        self.assertEqual(field_label, 'notes')
        
    def test_string_representation(self):
        management_period = ManagementPeriod.objects.get(id=1)
        self.assertEqual(str(management_period), '{0} at {1}'.format(management_period.manager, management_period.venue))
