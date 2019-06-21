import os
import shutil

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from accounts.models import CustomUser, HostProfile
from accounts.models import RegionalManagerProfile
from accounts.models import VenueManagerProfile
from locations.models import City, State, Zip, Region

from PIL import Image
from io import BytesIO

@override_settings(MEDIA_ROOT='temp_profile_images')
class CustomUserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.create(name='Meatballville')
        state = State.objects.create(name='New Jersey')
        zip = Zip.objects.create(code='07302')
        
        image = Image.new(mode='RGB', size=(200, 200))
        image_io = BytesIO()
        image.save(image_io, 'JPEG')
        image_io.seek(0)
        
        filename = 'test_image.jpg'
        test_image = SimpleUploadedFile(filename, image_io.read())
        
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti',
            mailing_city=city,
            mailing_state=state,
            mailing_zip=zip,
            profile_image=test_image,
            )
            
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('temp_profile_images')
        super().tearDownClass()

    def test_is_regional_manager_label(self):
        user = CustomUser.objects.get(pk=1)
        field_label = user._meta.get_field('is_regional_manager').verbose_name
        self.assertEqual(field_label, 'RM')

    def test_is_regional_manager_default_is_false(self):
        user = CustomUser.objects.get(pk=1)
        self.assertIs(user.is_regional_manager, False)

    def test_is_host_label(self):
        user = CustomUser.objects.get(pk=1)
        field_label = user._meta.get_field('is_host').verbose_name
        self.assertEqual(field_label, 'host')

    def test_is_host_default_is_false(self):
        user = CustomUser.objects.get(pk=1)
        self.assertIs(user.is_host, False)

    def test_is_venue_manager_label(self):
        user = CustomUser.objects.get(pk=1)
        field_label = user._meta.get_field('is_venue_manager').verbose_name
        self.assertEqual(field_label, 'VM')

    def test_is_venue_manager_default_is_false(self):
        user = CustomUser.objects.get(pk=1)
        self.assertIs(user.is_venue_manager, False)
        
    def test_secondary_email_label(self):
        user = CustomUser.objects.get(pk=1)
        field_label = user._meta.get_field('secondary_email').verbose_name
        self.assertEqual(field_label, 'secondary email')
        
    def test_secondary_email_max_length(self):
        user = CustomUser.objects.get(pk=1)
        max_length = user._meta.get_field('secondary_email').max_length
        self.assertEqual(max_length, 200)
        
    def test_mobile_number_label(self):
        user = CustomUser.objects.get(pk=1)
        field_label = user._meta.get_field('mobile_number').verbose_name
        self.assertEqual(field_label, 'mobile number')
        
    def test_mobile_number_max_length(self):
        user = CustomUser.objects.get(pk=1)
        max_length = user._meta.get_field('mobile_number').max_length
        self.assertEqual(max_length, 12)
        
    def test_work_number_label(self):
        user = CustomUser.objects.get(pk=1)
        field_label = user._meta.get_field('work_number').verbose_name
        self.assertEqual(field_label, 'work number')
        
    def test_work_number_max_length(self):
        user = CustomUser.objects.get(pk=1)
        max_length = user._meta.get_field('work_number').max_length
        self.assertEqual(max_length, 12)

    def test_mailing_address_label(self):
        user = CustomUser.objects.get(pk=1)
        field_label = user._meta.get_field('mailing_address').verbose_name
        self.assertEqual(field_label, 'mailing address')
        
    def test_mailing_address_max_length(self):
        user = CustomUser.objects.get(pk=1)
        max_length = user._meta.get_field('mailing_address').max_length
        self.assertEqual(max_length, 200)
        
    def test_mailing_additional_address_label(self):
        user = CustomUser.objects.get(pk=1)
        field_label = user._meta.get_field('mailing_additional_address').verbose_name
        self.assertEqual(field_label, 'mailing additional address')
        
    def test_mailing_additional_address_max_length(self):
        user = CustomUser.objects.get(pk=1)
        max_length = user._meta.get_field('mailing_additional_address').max_length
        self.assertEqual(max_length, 100)
        
    def test_mailing_city_label(self):
        user = CustomUser.objects.get(pk=1)
        field_label = user._meta.get_field('mailing_city').verbose_name
        self.assertEqual(field_label, 'mailing city')
        
    def test_mailing_city_delete_set_null(self):
        city = City.objects.get(pk=1)
        city.delete()
        user = CustomUser.objects.get(pk=1)
        count = CustomUser.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(user.mailing_city, None)
        
    def test_mailing_city_related_name_is_users(self):
        user = CustomUser.objects.get(pk=1)
        related_name = user.mailing_city._meta.get_field('users').related_name
        self.assertEqual(related_name, 'users')

    def test_mailing_state_label(self):
        user = CustomUser.objects.get(pk=1)
        field_label = user._meta.get_field('mailing_state').verbose_name
        self.assertEqual(field_label, 'mailing state')
        
    def test_mailing_state_delete_set_null(self):
        state = State.objects.get(pk='New Jersey')
        state.delete()
        user = CustomUser.objects.get(pk=1)
        count = CustomUser.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(user.mailing_state, None)
        
    def test_mailing_state_related_name_is_users(self):
        user = CustomUser.objects.get(pk=1)
        related_name = user.mailing_state._meta.get_field('users').related_name
        self.assertEqual(related_name, 'users')

    def test_mailing_zip_label(self):
        user = CustomUser.objects.get(pk=1)
        field_label = user._meta.get_field('mailing_zip').verbose_name
        self.assertEqual(field_label, 'mailing zip')
        
    def test_mailing_zip_delete_set_null(self):
        zip = Zip.objects.get(pk=1)
        zip.delete()
        user = CustomUser.objects.get(pk=1)
        count = CustomUser.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(user.mailing_zip, None)
        
    def test_mailing_zip_related_name_is_users(self):
        user = CustomUser.objects.get(pk=1)
        related_name = user.mailing_zip._meta.get_field('users').related_name
        self.assertEqual(related_name, 'users')
        
    def test_profile_image_upload_to_is_profile_images(self):
        user = CustomUser.objects.get(pk=1)
        filename = 'test_image.jpg'
        folder = 'profile_images'
        self.assertEqual(user.profile_image.name, '{0}/{1}'.format(folder, filename))

    def test_image_with_same_name_deletes_file(self):
        image = Image.new(mode='RGB', size=(200, 200))
        image_io = BytesIO()
        image.save(image_io, 'JPEG')
        image_io.seek(0)
        
        filename = 'test_image.jpg'
        test_image = SimpleUploadedFile(filename, image_io.read())
        user = CustomUser.objects.get(pk=1)
        
        total = 0
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            total += len(files)
            
        self.assertEqual(total, 1)
        
    def test_clean_no_role_designation_raises_validation_error(self):
        with self.assertRaises(ValidationError) as cm:
            user = CustomUser.objects.get(pk=1)
            user.full_clean()
        exception = cm.exception
        self.assertEqual(
            exception.messages, ['Please assign a role.'])
            
class HostProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.create(name='Meatballville')
        state = State.objects.create(name='New Jersey')
        zip = Zip.objects.create(code='07302')
        
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        host_profile = HostProfile.objects.create(
            user=user,
            residential_city=city,
            residential_state=state,
            residential_zip=zip,
            )

    def test_user_label(self):
        host_profile = HostProfile.objects.get(pk=1)
        field_label = host_profile._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_user_delete_cascade(self):
        user = CustomUser.objects.get(pk=1)
        user.delete()
        host_profile_count = HostProfile.objects.all().count()
        user_count = CustomUser.objects.all().count()
        self.assertEqual(host_profile_count, 0)
        self.assertEqual(user_count, 0)

    def test_user_related_name_is_host_profile(self):
        host_profile = HostProfile.objects.get(pk=1)
        related_name = host_profile.user._meta.get_field('host_profile').related_name
        self.assertEqual(related_name, 'host_profile')
        
    def test_has_event_label(self):
        host_profile = HostProfile.objects.get(pk=1)
        field_label = host_profile._meta.get_field('has_event').verbose_name
        self.assertEqual(field_label, 'has event')

    def test_has_event_default_is_true(self):
        host_profile = HostProfile.objects.get(pk=1)
        self.assertIs(host_profile.has_event, True)
        
    def test_residential_address_label(self):
        host_profile = HostProfile.objects.get(pk=1)
        field_label = host_profile._meta.get_field('residential_address').verbose_name
        self.assertEqual(field_label, 'residential address')
        
    def test_residential_address_max_length(self):
        host_profile = HostProfile.objects.get(pk=1)
        max_length = host_profile._meta.get_field('residential_address').max_length
        self.assertEqual(max_length, 200)
        
    def test_residential_additional_address_label(self):
        host_profile = HostProfile.objects.get(pk=1)
        field_label = host_profile._meta.get_field('residential_additional_address').verbose_name
        self.assertEqual(field_label, 'residential additional address')
        
    def test_residential_additional_address_max_length(self):
        host_profile = HostProfile.objects.get(pk=1)
        max_length = host_profile._meta.get_field('residential_additional_address').max_length
        self.assertEqual(max_length, 100)
        
    def test_residential_city_label(self):
        host_profile = HostProfile.objects.get(pk=1)
        field_label = host_profile._meta.get_field('residential_city').verbose_name
        self.assertEqual(field_label, 'residential city')
        
    def test_residential_city_delete_set_null(self):
        city = City.objects.get(pk=1)
        city.delete()
        host_profile = HostProfile.objects.get(pk=1)
        count = HostProfile.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(host_profile.residential_city, None)
        
    def test_residential_city_related_name_is_host_profiles(self):
        host_profile = HostProfile.objects.get(pk=1)
        related_name = host_profile.residential_city._meta.get_field('host_profiles').related_name
        self.assertEqual(related_name, 'host_profiles')

    def test_residential_state_label(self):
        host_profile = HostProfile.objects.get(pk=1)
        field_label = host_profile._meta.get_field('residential_state').verbose_name
        self.assertEqual(field_label, 'residential state')
        
    def test_residential_state_delete_set_null(self):
        state = State.objects.get(pk='New Jersey')
        state.delete()
        host_profile = HostProfile.objects.get(pk=1)
        count = HostProfile.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(host_profile.residential_state, None)
        
    def test_residential_state_related_name_is_host_profiles(self):
        host_profile = HostProfile.objects.get(pk=1)
        related_name = host_profile.residential_state._meta.get_field('host_profiles').related_name
        self.assertEqual(related_name, 'host_profiles')

    def test_residential_zip_label(self):
        host_profile = HostProfile.objects.get(pk=1)
        field_label = host_profile._meta.get_field('residential_zip').verbose_name
        self.assertEqual(field_label, 'residential zip')
        
    def test_residential_zip_delete_set_null(self):
        zip = Zip.objects.get(pk=1)
        zip.delete()
        host_profile = HostProfile.objects.get(pk=1)
        count = HostProfile.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(host_profile.residential_zip, None)
        
    def test_residential_zip_related_name_is_host_profiles(self):
        host_profile = HostProfile.objects.get(pk=1)
        related_name = host_profile.residential_zip._meta.get_field('host_profiles').related_name
        self.assertEqual(related_name, 'host_profiles')

    def test_base_teams_label(self):
        host_profile = HostProfile.objects.get(pk=1)
        field_label = host_profile._meta.get_field('base_teams').verbose_name
        self.assertEqual(field_label, 'base teams')
        
    def test_base_teams_default_is_five(self):
        host_profile = HostProfile.objects.get(pk=1)
        self.assertEqual(host_profile.base_teams, 5)
        
    def test_base_rate_label(self):
        host_profile = HostProfile.objects.get(pk=1)
        field_label = host_profile._meta.get_field('base_rate').verbose_name
        self.assertEqual(field_label, 'base rate')
        
    def test_base_rate_max_digits_is_six(self):
        host_profile = HostProfile.objects.get(pk=1)
        max_digits = host_profile._meta.get_field('base_rate').max_digits
        self.assertEqual(max_digits, 5)
        
    def test_base_rate_decimal_places_is_two(self):
        host_profile = HostProfile.objects.get(pk=1)
        decimal_places = host_profile._meta.get_field('base_rate').decimal_places
        self.assertEqual(decimal_places, 2)
        
    def test_base_rate_default_is_fifty(self):
        host_profile = HostProfile.objects.get(pk=1)
        self.assertEqual(host_profile.base_rate, 50)
        
    def test_incremental_teams_label(self):
        host_profile = HostProfile.objects.get(pk=1)
        field_label = host_profile._meta.get_field('incremental_teams').verbose_name
        self.assertEqual(field_label, 'incremental teams')
        
    def test_incremental_teams_default_is_one(self):
        host_profile = HostProfile.objects.get(pk=1)
        self.assertEqual(host_profile.incremental_teams, 1)
        
    def test_incremental_rate_label(self):
        host_profile = HostProfile.objects.get(pk=1)
        field_label = host_profile._meta.get_field('incremental_rate').verbose_name
        self.assertEqual(field_label, 'incremental rate')
        
    def test_incremental_rate_max_digits_is_six(self):
        host_profile = HostProfile.objects.get(pk=1)
        max_digits = host_profile._meta.get_field('incremental_rate').max_digits
        self.assertEqual(max_digits, 5)
        
    def test_incremental_rate_decimal_places_is_two(self):
        host_profile = HostProfile.objects.get(pk=1)
        decimal_places = host_profile._meta.get_field('incremental_rate').decimal_places
        self.assertEqual(decimal_places, 2)
        
    def test_incremental_rate_default_is_five(self):
        host_profile = HostProfile.objects.get(pk=1)
        self.assertEqual(host_profile.incremental_rate, 2)
        
    def test_host_profile_str_is_user_username(self):
        host_profile = HostProfile.objects.get(pk=1)
        self.assertEqual(str(host_profile), host_profile.user.username)
        
    # def test_map_link(self):
    
class RegionalManagerProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        region = Region.objects.create(name='NE')

        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        regional_manager_profile = RegionalManagerProfile.objects.create(
            user=user,
            region=region,
            )

    def test_user_label(self):
        regional_manager_profile = RegionalManagerProfile.objects.get(pk=1)
        field_label = regional_manager_profile._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_user_delete_cascade(self):
        user = CustomUser.objects.get(pk=1)
        user.delete()
        regional_manager_profile_count = RegionalManagerProfile.objects.all().count()
        user_count = CustomUser.objects.all().count()
        self.assertEqual(regional_manager_profile_count, 0)
        self.assertEqual(user_count, 0)

    def test_user_related_name_is_regional_manager_profile(self):
        regional_manager_profile = RegionalManagerProfile.objects.get(pk=1)
        related_name = regional_manager_profile.user._meta.get_field('regional_manager_profile').related_name
        self.assertEqual(related_name, 'regional_manager_profile')
        
    def test_region_label(self):
        regional_manager_profile = RegionalManagerProfile.objects.get(pk=1)
        field_label = regional_manager_profile._meta.get_field('region').verbose_name
        self.assertEqual(field_label, 'region')
        
    def test_region_delete_set_null(self):
        region = Region.objects.get(name='NE')
        region.delete()
        regional_manager_profile = RegionalManagerProfile.objects.get(pk=1)
        count = RegionalManagerProfile.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(regional_manager_profile.region, None)
        
    def test_region_related_name_is_regional_manager_profiles(self):
        regional_manager_profile = RegionalManagerProfile.objects.get(pk=1)
        related_name = regional_manager_profile.region._meta.get_field('regional_manager_profiles').related_name
        self.assertEqual(related_name, 'regional_manager_profiles')
        
    def test_weekly_pay_label(self):
        regional_manager_profile = RegionalManagerProfile.objects.get(pk=1)
        field_label = regional_manager_profile._meta.get_field('weekly_pay').verbose_name
        self.assertEqual(field_label, 'weekly pay')
        
    def test_weekly_pay_max_digits_is_six(self):
        regional_manager_profile = RegionalManagerProfile.objects.get(pk=1)
        max_digits = regional_manager_profile._meta.get_field('weekly_pay').max_digits
        self.assertEqual(max_digits, 5)
        
    def test_weekly_pay_decimal_places_is_two(self):
        regional_manager_profile = RegionalManagerProfile.objects.get(pk=1)
        decimal_places = regional_manager_profile._meta.get_field('weekly_pay').decimal_places
        self.assertEqual(decimal_places, 2)
        
    def test_regional_manager_profile_str_is_user_username(self):
        regional_manager_profile = RegionalManagerProfile.objects.get(pk=1)
        self.assertEqual(str(regional_manager_profile), regional_manager_profile.user.username)
        
class VenueManagerProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        venue_manager_profile = VenueManagerProfile.objects.create(user=user)
    
    def test_user_label(self):
        venue_manager_profile = VenueManagerProfile.objects.get(pk=1)
        field_label = venue_manager_profile._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_user_delete_cascade(self):
        user = CustomUser.objects.get(pk=1)
        user.delete()
        venue_manager_profile_count = VenueManagerProfile.objects.all().count()
        user_count = CustomUser.objects.all().count()
        self.assertEqual(venue_manager_profile_count, 0)
        self.assertEqual(user_count, 0)
        
    def test_best_reached_by_max_length(self):
        venue_manager_profile = VenueManagerProfile.objects.get(pk=1)
        max_length = venue_manager_profile._meta.get_field('best_reached_by').max_length
        self.assertEqual(max_length, 5)
        
    def test_choice_for_best_reached_by_values_and_readable_names(self):
        venue_manager_profile = VenueManagerProfile.objects.get(pk=1)
        field_choices = venue_manager_profile._meta.get_field('best_reached_by').choices
        expected_value = ['Cell', 'Venue', 'Email']
        expected_human_readable = ['Cellphone', 'Venue phone', 'Email']
        for index, (value, human_readable) \
            in enumerate(field_choices):
            self.assertEqual(value, expected_value[index])
            self.assertEqual(human_readable, expected_human_readable[index])
            
    def test_venue_manager_profile_str_is_user_username(self):
        venue_manager_profile = VenueManagerProfile.objects.get(pk=1)
        self.assertEqual(str(venue_manager_profile), venue_manager_profile.user.username)
        
    def test_display_preferred_communication_cell(self):
        user = CustomUser.objects.get(pk=1)
        user.mobile_number = '123456789'
        user.save()
        venue_manager_profile = VenueManagerProfile.objects.get(pk=1)
        venue_manager_profile.best_reached_by = 'Cell'
        self.assertEqual(
            venue_manager_profile.display_preferred_communication(), '123456789')
            
    def test_display_preferred_communication_venue(self):
        user = CustomUser.objects.get(pk=1)
        user.work_number = '987654321'
        user.save()
        venue_manager_profile = VenueManagerProfile.objects.get(pk=1)
        venue_manager_profile.best_reached_by = 'Venue'
        self.assertEqual(
            venue_manager_profile.display_preferred_communication(), '987654321')
            
    def test_display_preferred_communication_email(self):
        user = CustomUser.objects.get(pk=1)
        user.email = 'user@email.com'
        user.save()
        venue_manager_profile = VenueManagerProfile.objects.get(pk=1)
        venue_manager_profile.best_reached_by = 'Email'
        self.assertEqual(
            venue_manager_profile.display_preferred_communication(), 'user@email.com')
            
    def test_display_preferred_communication_short_description(self):
        venue_manager_profile = VenueManagerProfile.objects.get(pk=1)
        short_description = venue_manager_profile.display_preferred_communication.short_description
        self.assertEqual(short_description, 'Number or Email')