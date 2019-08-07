import calendar
import datetime
import os
import shutil

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import CustomUser
from locations.models import Venue
from schedule.models import Day, Time, Event, EventImage, EventOccurrence

from PIL import Image
from io import BytesIO

class DayModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        day = Day.objects.create(day=1)
        
    def test_day_label(self):
        day = Day.objects.get(day=1)
        field_label = day._meta.get_field('day').verbose_name
        self.assertEqual(field_label, 'day')

    def test_day_choices_are_0_mon_through_6_sun(self):
        day = Day.objects.get(day=1)
        field_choices = day._meta.get_field('day').choices
        expected_value = [0, 1, 2, 3, 4, 5, 6]
        expected_human_readable = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for index, (value, human_readable) in enumerate(field_choices):
            self.assertEqual(value, expected_value[index])
            self.assertEqual(human_readable, expected_human_readable[index])
    
    def test_day_is_primary_key(self):
        day = Day.objects.get(day=1)
        self.assertEqual(day.day, day.pk)
    
    def test_day_str_returns_abbr_day_of_week(self):
        day = Day.objects.get(day=1)
        self.assertEqual(str(day), calendar.day_abbr[day.day])
        
class TimeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        time = Time.objects.create(time=datetime.time(20,30))
        
    def test_time_label(self):
        time = Time.objects.get(time=datetime.time(20,30))
        field_label = time._meta.get_field('time').verbose_name
        self.assertEqual(field_label, 'time')
        
    def test_time_set_to_default(self):
        time = Time.objects.create()
        self.assertEqual(time.time, time.DEFAULT_TIME)
        
    def test_time_default_is_set_to_eight_oclock(self):
        time = Time.objects.create()
        self.assertEqual(time.DEFAULT_TIME, datetime.time(20,0))
        
    def test_time_is_primary_key(self):
        time = Time.objects.get(time=datetime.time(20,30))
        self.assertEqual(time.time, time.pk)
    
    def test_time_str_returns_am_pm(self):
        time = Time.objects.get(time=datetime.time(20,30))
        self.assertEqual(str(time), time.time.strftime('%I:%M %p'))
        
class EventModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        venue = Venue.objects.create(name='The Meatballery')
        host = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        day = Day.objects.create(day=1)
        time = Time.objects.create(time=datetime.time(20,0))
        event = Event.objects.create(
            venue=venue,
            host=host,
            day=day,
            time=time,
            )
            
    def test_venue_label(self):
        event = Event.objects.get(pk=1)
        field_label = event._meta.get_field('venue').verbose_name
        self.assertEqual(field_label, 'venue')
        
    def test_venue_null_on_delete(self):
        venue = Venue.objects.get(pk=1)
        venue.delete()
        venue_count = Venue.objects.all().count()
        event_count = Event.objects.all().count()
        event = Event.objects.get(pk=1)
        self.assertEqual(venue_count, 0)
        self.assertEqual(event_count, 1)
        self.assertEqual(event.venue, None)
        
    def test_venue_related_name_is_events(self):
        event = Event.objects.get(pk=1)
        related_name = event.venue._meta.get_field('events').related_name
        self.assertEqual(related_name, 'events')
    
    def test_host_label(self):
        event = Event.objects.get(pk=1)
        field_label = event._meta.get_field('host').verbose_name
        self.assertEqual(field_label, 'host')
        
    def test_host_null_on_delete(self):
        host = CustomUser.objects.get(pk=1)
        host.delete()
        host_count = CustomUser.objects.all().count()
        event_count = Event.objects.all().count()
        event = Event.objects.get(pk=1)
        self.assertEqual(host_count, 0)
        self.assertEqual(event_count, 1)
        self.assertEqual(event.host, None)
        
    def test_host_related_name_is_events(self):
        event = Event.objects.get(pk=1)
        related_name = event.host._meta.get_field('events').related_name
        self.assertEqual(related_name, 'events')
        
    def test_day_label(self):
        event = Event.objects.get(pk=1)
        field_label = event._meta.get_field('day').verbose_name
        self.assertEqual(field_label, 'day')
        
    def test_day_null_on_delete(self):
        day = Day.objects.get(day=1)
        day.delete()
        day_count = Day.objects.all().count()
        event_count = Event.objects.all().count()
        event = Event.objects.get(pk=1)
        self.assertEqual(day_count, 0)
        self.assertEqual(event_count, 1)
        self.assertEqual(event.day, None)
        
    def test_day_related_name_is_events(self):
        event = Event.objects.get(pk=1)
        related_name = event.day._meta.get_field('events').related_name
        self.assertEqual(related_name, 'events')
        
    def test_time_label(self):
        event = Event.objects.get(pk=1)
        field_label = event._meta.get_field('time').verbose_name
        self.assertEqual(field_label, 'time')
        
    def test_time_null_on_delete(self):
        time = Time.objects.get(time=datetime.time(20,0))
        time.delete()
        time_count = Time.objects.all().count()
        event_count = Event.objects.all().count()
        event = Event.objects.get(pk=1)
        self.assertEqual(time_count, 0)
        self.assertEqual(event_count, 1)
        self.assertEqual(event.time, None)
        
    def test_time_related_name_is_events(self):
        event = Event.objects.get(pk=1)
        related_name = event.time._meta.get_field('events').related_name
        self.assertEqual(related_name, 'events')
        
    def test_start_date_label(self):
        event = Event.objects.get(pk=1)
        field_label = event._meta.get_field('start_date').verbose_name
        self.assertEqual(field_label, 'start date')
        
    def test_end_date_label(self):
        event = Event.objects.get(pk=1)
        field_label = event._meta.get_field('end_date').verbose_name
        self.assertEqual(field_label, 'end date')
        
    def test_first_place_prize_label(self):
        event = Event.objects.get(pk=1)
        field_label = event._meta.get_field('first_place_prize').verbose_name
        self.assertEqual(field_label, 'first place prize')
        
    def test_first_place_prize_max_length(self):
        event = Event.objects.get(pk=1)
        max_length = event._meta.get_field('first_place_prize').max_length
        self.assertEqual(max_length, 50)
        
    def test_second_place_prize_label(self):
        event = Event.objects.get(pk=1)
        field_label = event._meta.get_field('second_place_prize').verbose_name
        self.assertEqual(field_label, 'second place prize')
        
    def test_second_place_prize_max_length(self):
        event = Event.objects.get(pk=1)
        max_length = event._meta.get_field('second_place_prize').max_length
        self.assertEqual(max_length, 50)
        
    def test_third_place_prize_label(self):
        event = Event.objects.get(pk=1)
        field_label = event._meta.get_field('third_place_prize').verbose_name
        self.assertEqual(field_label, 'third place prize')
        
    def test_third_place_prize_max_length(self):
        event = Event.objects.get(pk=1)
        max_length = event._meta.get_field('third_place_prize').max_length
        self.assertEqual(max_length, 50)
        
    def test_additional_prize_info_label(self):
        event = Event.objects.get(pk=1)
        field_label = event._meta.get_field('additional_prize_info').verbose_name
        self.assertEqual(field_label, 'additional prize info')
        
    def test_status_label(self):
        event = Event.objects.get(pk=1)
        field_label = event._meta.get_field('status').verbose_name
        self.assertEqual(field_label, 'status')
        
    def test_status_max_length(self):
        event = Event.objects.get(pk=1)
        max_length = event._meta.get_field('status').max_length
        self.assertEqual(max_length, 1)
        
    def test_status_choices_are_starting_active_ending_terminated(self):
        event = Event.objects.get(day=1)
        field_choices = event._meta.get_field('status').choices
        expected_value = ['S', 'A', 'E', 'T']
        expected_human_readable = ['Starting', 'Active', 'Ending', 'Terminated']
        for index, (value, human_readable) in enumerate(field_choices):
            self.assertEqual(value, expected_value[index])
            self.assertEqual(human_readable, expected_human_readable[index])
            
    def test_request_future_restart_label(self):
        event = Event.objects.get(pk=1)
        field_label = event._meta.get_field('request_future_restart').verbose_name
        self.assertEqual(field_label, 'request future restart')
        
    def test_request_future_restart_default_false(self):
        event = Event.objects.get(pk=1)
        self.assertIs(event.request_future_restart, False)
        
    def test_base_teams_label(self):
        event = Event.objects.get(pk=1)
        field_label = event._meta.get_field('base_teams').verbose_name
        self.assertEqual(field_label, 'base teams')
        
    def test_base_teams_default_is_five(self):
        event = Event.objects.get(pk=1)
        self.assertEqual(event.base_teams, 5)
        
    def test_base_rate_label(self):
        event = Event.objects.get(pk=1)
        field_label = event._meta.get_field('base_rate').verbose_name
        self.assertEqual(field_label, 'base rate')
        
    def test_base_rate_max_digits_is_six(self):
        event = Event.objects.get(pk=1)
        max_digits = event._meta.get_field('base_rate').max_digits
        self.assertEqual(max_digits, 6)
        
    def test_base_rate_decimal_places_is_two(self):
        event = Event.objects.get(pk=1)
        decimal_places = event._meta.get_field('base_rate').decimal_places
        self.assertEqual(decimal_places, 2)
        
    def test_base_rate_default_is_one_hundred_twenty_five(self):
        event = Event.objects.get(pk=1)
        self.assertEqual(event.base_rate, 125)
        
    def test_incremental_teams_label(self):
        event = Event.objects.get(pk=1)
        field_label = event._meta.get_field('incremental_teams').verbose_name
        self.assertEqual(field_label, 'incremental teams')
        
    def test_incremental_teams_default_is_one(self):
        event = Event.objects.get(pk=1)
        self.assertEqual(event.incremental_teams, 1)
        
    def test_incremental_rate_label(self):
        event = Event.objects.get(pk=1)
        field_label = event._meta.get_field('incremental_rate').verbose_name
        self.assertEqual(field_label, 'incremental rate')
        
    def test_incremental_rate_max_digits_is_six(self):
        event = Event.objects.get(pk=1)
        max_digits = event._meta.get_field('incremental_rate').max_digits
        self.assertEqual(max_digits, 6)
        
    def test_incremental_rate_decimal_places_is_two(self):
        event = Event.objects.get(pk=1)
        decimal_places = event._meta.get_field('incremental_rate').decimal_places
        self.assertEqual(decimal_places, 2)
        
    def test_incremental_rate_default_is_five(self):
        event = Event.objects.get(pk=1)
        self.assertEqual(event.incremental_rate, 5)
        
    def test_event_str_is_venue_day_and_time(self):
        event = Event.objects.get(pk=1)
        self.assertEqual(str(event), '{0} ({1} at {2})'.format(
            event.venue, event.day, event.time))
            
    def test_event_absolute_url(self):
        event = Event.objects.get(pk=1)
        self.assertEqual(event.get_absolute_url(), reverse('event-detail', args=[event.pk]))
        
    def test_event_clean_start_date_but_no_day_gives_error(self):
        with self.assertRaises(ValidationError) as cm:
            event =  Event.objects.get(pk=1)
            event.day = None
            event.start_date = datetime.date.today()
            event.full_clean()
        
        exception = cm.exception
        self.assertEqual(exception.messages, ['Please specify the day of the week.'])
    
    def test_event_clean_end_date_but_no_day_gives_error(self):
        with self.assertRaises(ValidationError) as cm:
            event =  Event.objects.get(pk=1)
            event.day = None
            event.end_date = datetime.date.today()
            event.full_clean()
        
        exception = cm.exception
        self.assertEqual(exception.messages, ['Please specify the day of the week.'])
    
    def test_event_clean_with_day_start_date_does_not_coincide_gives_error(self):
        today = datetime.date.today()
        today_day = today.weekday() # 0 if today is a monday, etc.
        day, created = Day.objects.get_or_create(day=today_day)
        
        tomorrow_date = today + datetime.timedelta(days=1)
       
        with self.assertRaises(ValidationError) as cm:
            event =  Event.objects.get(pk=1)
            event.day = day
            event.start_date = tomorrow_date
            event.full_clean()
        
        exception = cm.exception
        start_date_day = calendar.day_abbr[event.start_date.weekday()]
        self.assertEqual(
            exception.messages,
            ['The {0} date and day of the week do not coincide. '
            'Did you mean {1}?'.format('start', start_date_day)])
    
    def test_event_clean_with_day_end_date_does_not_coincide_gives_error(self):
        today = datetime.date.today()
        today_day = today.weekday() # 0 if today is a monday, etc.
        day, created = Day.objects.get_or_create(day=today_day)
        
        tomorrow_date = today + datetime.timedelta(days=1)
       
        with self.assertRaises(ValidationError) as cm:
            event =  Event.objects.get(pk=1)
            event.day = day
            event.end_date = tomorrow_date
            event.full_clean()
        
        exception = cm.exception
        end_date_day = calendar.day_abbr[event.end_date.weekday()]
        self.assertEqual(
            exception.messages,
            ['The {0} date and day of the week do not coincide. '
            'Did you mean {1}?'.format('end', end_date_day)])
    
    def test_event_clean_with_day_end_date_earlier_than_start_date_gives_error(self):
        today = datetime.date.today()
        today_day = today.weekday() # 0 if today is a monday, etc.
        day, created = Day.objects.get_or_create(day=today_day)
        
        last_week = today - datetime.timedelta(days=7)
        
        with self.assertRaises(ValidationError) as cm:
            event =  Event.objects.get(pk=1)
            event.day = day
            event.start_date = today
            event.end_date = last_week
            event.full_clean()
        
        exception = cm.exception
        self.assertEqual(
            exception.messages,
            ['The start date is later than the end date. '
            'Please correct.'])
            
    def test_event_clean_start_date_in_future_labeled_as_starting(self):
        today = datetime.date.today()

        tomorrow = today + datetime.timedelta(days=1)
        tomorrow_day = tomorrow.weekday()
        day, created = Day.objects.get_or_create(day=tomorrow_day)
        
        event = Event.objects.get(pk=1)
        event.day = day
        event.start_date = tomorrow
        event.full_clean()
        self.assertEqual(event.status, 'S')
    
    def test_event_clean_start_date_in_past_labeled_as_active(self):
        today = datetime.date.today()

        yesterday = today - datetime.timedelta(days=1)
        yesterday_day = yesterday.weekday()
        day, created = Day.objects.get_or_create(day=yesterday_day)
        
        event = Event.objects.get(pk=1)
        event.day = day
        event.start_date = yesterday
        event.full_clean()
        self.assertEqual(event.status, 'A')
    
    def test_event_clean_end_date_approaching_labeled_as_ending(self):
        today = datetime.date.today()

        two_weeks_out = today + datetime.timedelta(days=13)
        two_weeks_out_day = two_weeks_out.weekday()
        day, created = Day.objects.get_or_create(day=two_weeks_out_day)
        
        event = Event.objects.get(pk=1)
        event.day = day
        event.end_date = two_weeks_out
        event.full_clean()
        self.assertEqual(event.status, 'E')
    
    def test_event_clean_end_date_in_past_labeled_as_terminated(self):
        today = datetime.date.today()

        yesterday = today - datetime.timedelta(days=1)
        yesterday_day = yesterday.weekday()
        day, created = Day.objects.get_or_create(day=yesterday_day)
        
        event = Event.objects.get(pk=1)
        event.day = day
        event.end_date = yesterday
        event.full_clean()
        self.assertEqual(event.status, 'T')

@override_settings(MEDIA_ROOT='temp_event_image_files')
class EventImageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        venue = Venue.objects.create(name='The Meatballery')
        event = Event.objects.create(venue=venue)
        
        image = Image.new(mode='RGB', size=(200, 200))
        image_io = BytesIO()
        image.save(image_io, 'JPEG')
        image_io.seek(0)
        
        filename = 'test_image.jpg'
        test_image = SimpleUploadedFile(filename, image_io.read())
        
        event_image = EventImage.objects.create(event=event, image=test_image)
    
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('temp_event_image_files')
        super().tearDownClass()

    def test_event_label(self):
        event_image = EventImage.objects.get(pk=1)
        field_label = event_image._meta.get_field('event').verbose_name
        self.assertEqual(field_label, 'event')
        
    def test_event_null_on_delete(self):
        event = Event.objects.get(pk=1)
        event.delete()
        event_count = Event.objects.all().count()
        event_image_count = EventImage.objects.all().count()
        event_image = EventImage.objects.get(pk=1)
        self.assertEqual(event_count, 0)
        self.assertEqual(event_image_count, 1)
        self.assertEqual(event_image.event, None)
        
    def test_event_related_name_is_events(self):
        event_image = EventImage.objects.get(pk=1)
        related_name = event_image.event._meta.get_field('images').related_name
        self.assertEqual(related_name, 'images')
        
    def test_image_label(self):
        event_image = EventImage.objects.get(pk=1)
        field_label = event_image._meta.get_field('image').verbose_name
        self.assertEqual(field_label, 'image')
    
    def test_image_upload_to_is_event_images_venue_name_file(self):
        event_image = EventImage.objects.get(pk=1)
        filename = 'test_image.jpg'
        folder = 'event_images'
        sub_folder = str(event_image.event.venue.name).replace(" ", "_").replace("\'", "").lower()
        self.assertEqual(
            event_image.image.name,
            '{0}/{1}/{2}'.format(folder, sub_folder, filename))

    def test_image_with_same_name_deletes_record(self):
        image = Image.new(mode='RGB', size=(200, 200))
        image_io = BytesIO()
        image.save(image_io, 'JPEG')
        image_io.seek(0)
        
        filename = 'test_image.jpg'
        test_image = SimpleUploadedFile(filename, image_io.read())
        event = Event.objects.get(pk=1)
        event_image_2 = EventImage.objects.create(event=event, image=test_image)
        self.assertEqual(EventImage.objects.all().count(), 1)
    
    def test_image_with_same_name_deletes_file(self):
        image = Image.new(mode='RGB', size=(200, 200))
        image_io = BytesIO()
        image.save(image_io, 'JPEG')
        image_io.seek(0)
        
        filename = 'test_image.jpg'
        test_image = SimpleUploadedFile(filename, image_io.read())
        event = Event.objects.get(pk=1)
        event_image_2 = EventImage.objects.create(event=event, image=test_image)
        
        total = 0
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            total += len(files)
            
        self.assertEqual(total, 1)

    # def test_image_saves_rotated_minimized_and_cropped(self):

@override_settings(MEDIA_ROOT='temp_event_occurrence_files')
class EventOccurrenceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        host = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        venue = Venue.objects.create(name='The Meatballery')
        day = Day.objects.create(day=1)
        time = Time.objects.create(time=datetime.time(20,0))
        event = Event.objects.create(
            day=day, time=time, venue=venue, host=host)
        test_file = SimpleUploadedFile('test_file.txt', b'test file text')
        EventOccurrence.objects.create(
            event=event, day=day, time=time, 
            date=datetime.date(year=2019, month=5, day=14),
            scoresheet=test_file,
            host=host)
            
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('temp_event_occurrence_files')
        super().tearDownClass()

    def test_event_label(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        field_label = event_occurrence._meta.get_field('event').verbose_name
        self.assertEqual(field_label, 'event')
        
    def test_event_delete_set_null(self):
        event = Event.objects.get(pk=1)
        event.delete()
        event_occurrence = EventOccurrence.objects.get(pk=1)
        count = EventOccurrence.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(event_occurrence.event, None)
        
    def test_event_related_name_is_event_occurrences(self):
        event_occurrence = EventOccurrence.objects.get(id=1)
        related_name = event_occurrence.event._meta.get_field('event_occurrences').related_name
        self.assertEqual(related_name, 'event_occurrences')
        
    def test_day_label(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        field_label = event_occurrence._meta.get_field('day').verbose_name
        self.assertEqual(field_label, 'day')
        
    def test_day_delete_set_null(self):
        day = Day.objects.get(pk=1)
        day.delete()
        event_occurrence = EventOccurrence.objects.get(pk=1)
        count = EventOccurrence.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(event_occurrence.day, None)
        
    def test_day_related_name_is_event_occurrences(self):
        event_occurrence = EventOccurrence.objects.get(id=1)
        related_name = event_occurrence.day._meta.get_field('event_occurrences').related_name
        self.assertEqual(related_name, 'event_occurrences')
        
    def test_time_label(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        field_label = event_occurrence._meta.get_field('time').verbose_name
        self.assertEqual(field_label, 'time')
        
    def test_time_delete_set_null(self):
        time = Time.objects.get(time=datetime.time(20,0))
        time.delete()
        event_occurrence = EventOccurrence.objects.get(pk=1)
        count = EventOccurrence.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(event_occurrence.time, None)
        
    def test_time_related_name_is_event_occurrences(self):
        event_occurrence = EventOccurrence.objects.get(id=1)
        related_name = event_occurrence.time._meta.get_field('event_occurrences').related_name
        self.assertEqual(related_name, 'event_occurrences')
        
    def test_date_label(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        field_label = event_occurrence._meta.get_field('date').verbose_name
        self.assertEqual(field_label, 'date')
        
    def test_host_label(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        field_label = event_occurrence._meta.get_field('host').verbose_name
        self.assertEqual(field_label, 'host')
        
    def test_host_delete_set_null(self):
        host = CustomUser.objects.get(pk=1)
        host.delete()
        event_occurrence = EventOccurrence.objects.get(pk=1)
        count = EventOccurrence.objects.all().count()
        self.assertEqual(count, 1)
        self.assertEqual(event_occurrence.host, None)
        
    def test_host_related_name_is_event_occurrences(self):
        event_occurrence = EventOccurrence.objects.get(id=1)
        related_name = event_occurrence.time._meta.get_field('event_occurrences').related_name
        self.assertEqual(related_name, 'event_occurrences')

    def test_change_host_label(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        field_label = event_occurrence._meta.get_field('change_host').verbose_name
        self.assertEqual(field_label, 'change host')
        
    def test_change_host_default_false(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        self.assertIs(event_occurrence.change_host, False)

    def test_status_label(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        field_label = event_occurrence._meta.get_field('status').verbose_name
        self.assertEqual(field_label, 'status')
        
    def test_status_max_length(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        max_length = event_occurrence._meta.get_field('status').max_length
        self.assertEqual(max_length, 7)
        
    def test_status_default_is_game(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        self.assertEqual(event_occurrence.status, 'Game')
        
    def test_choice_for_status_values_and_readable_names_are_game_and_no_game(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        field_choices = event_occurrence._meta.get_field('status').choices
        expected_value = ['Game', 'No Game']
        expected_human_readable = ['Game', 'No Game']
        for index, (value, human_readable) \
            in enumerate(field_choices):
            self.assertEqual(value, expected_value[index])
            self.assertEqual(human_readable, expected_human_readable[index])

    def test_cancellation_reason_label(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        field_label = event_occurrence._meta.get_field('cancellation_reason').verbose_name
        self.assertEqual(field_label, 'cancellation reason')
        
    def test_cancellation_reason_max_length(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        max_length = event_occurrence._meta.get_field('cancellation_reason').max_length
        self.assertEqual(max_length, 20)
        
    def test_choice_for_cancellation_reason_values_and_readable_names(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        field_choices = event_occurrence._meta.get_field('cancellation_reason').choices
        expected_value = [
            'Low/No Attendance', 'Alternate Event', 'Holiday',
            'Inclement Weather', 'Renovations', 'Emergency', 'Other'
            ]
        expected_human_readable = [
            'Low or No Attendance', 'Alternate Event', 'Holiday',
            'Inclement Weather', 'Renovations', 'Emergency', 'Other'
            ]
        for index, (value, human_readable) \
            in enumerate(field_choices):
            self.assertEqual(value, expected_value[index])
            self.assertEqual(human_readable, expected_human_readable[index])
            
    def test_cancellation_reason_help_text(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        help_text = event_occurrence._meta.get_field('cancellation_reason').help_text
        self.assertEqual(help_text, 'Only required if "No Game" was chosen.')
        
    def test_cancelled_ahead_label(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        field_label = event_occurrence._meta.get_field('cancelled_ahead').verbose_name
        self.assertEqual(field_label, 'cancelled ahead')
        
    def test_cancelled_ahead_default_is_false(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        self.assertIs(event_occurrence.cancelled_ahead, False)

    def test_time_started_label(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        field_label = event_occurrence._meta.get_field('time_started').verbose_name
        self.assertEqual(field_label, 'time started')
        
    def test_time_started_help_text(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        help_text = event_occurrence._meta.get_field('time_started').help_text
        self.assertEqual(help_text, 'ex. 08:10 PM. Only required if "Game" was chosen.')

    def test_time_ended_label(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        field_label = event_occurrence._meta.get_field('time_ended').verbose_name
        self.assertEqual(field_label, 'time ended')
        
    def test_time_ended_help_text(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        help_text = event_occurrence._meta.get_field('time_ended').help_text
        self.assertEqual(help_text, 'ex. 10:05 PM. Only required if "Game" was chosen.')

    def test_number_of_teams_label(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        field_label = event_occurrence._meta.get_field('number_of_teams').verbose_name
        self.assertEqual(field_label, 'number of teams')
        
    def test_number_of_teams_help_text(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        help_text = event_occurrence._meta.get_field('number_of_teams').help_text
        self.assertEqual(help_text, 'Only required if "Game" was chosen.')

    def test_scoresheet_label(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        field_label = event_occurrence._meta.get_field('scoresheet').verbose_name
        self.assertEqual(field_label, 'scoresheet')

    def test_scoresheet_uploads_to_scoresheets_venue_occurrence_date_filename(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        filename = 'test_file.txt'
        folder = 'scoresheets'
        sub_folder = str(event_occurrence.event.venue.name).replace(" ", "_").replace("\'", "").lower()
        occurrence_date = event_occurrence.date
        self.assertEqual(
            event_occurrence.scoresheet.name,
            '{0}/{1}/{2}_{3}'.format(folder, sub_folder, occurrence_date, filename))
    
    def test_image_with_same_name_deletes_file(self):
        test_file = SimpleUploadedFile('test_file.txt', b'test file text')
        event_occurrence = EventOccurrence.objects.get(pk=1)
        event_occurrence.scoresheet = test_file
        event_occurrence.save()
        
        total = 0
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            total += len(files)
        self.assertEqual(total, 1)

    def test_notes_label(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        field_label = event_occurrence._meta.get_field('notes').verbose_name
        self.assertEqual(field_label, 'notes')
        
    def test_notes_help_text(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        help_text = event_occurrence._meta.get_field('notes').help_text
        self.assertEqual(
            help_text,
            'Please include notes about the game here. '
            'For example, technical problems, '
            'customer issues, suggestions, etc...')
            
    def test_string_representation_is_event(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        self.assertEqual(
            str(event_occurrence),
            '{0} - {1} ({2})'.format(
                event_occurrence.event, event_occurrence.date,
                event_occurrence.host))
                
    def test_is_different_time(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        time = Time.objects.create(time=datetime.time(20,30))
        event_occurrence.time = time
        self.assertTrue(event_occurrence.is_different_time)

    def test_is_different_day(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        event_occurrence.day = Day.objects.create(day=2)
        self.assertTrue(event_occurrence.is_different_day)

    def test_is_different_host(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        event_occurrence.host = CustomUser.objects.create_user(
            username='matt', password='Ilovemeatballs')
        self.assertTrue(event_occurrence.is_different_host)
        
    def test_is_complete_game_no_data_is_false(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        event_occurrence.status = 'Game'
        self.assertFalse(event_occurrence.is_complete)

    def test_is_complete_game_with_complete_data_is_true(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        event_occurrence.status = 'Game'
        event_occurrence.time_started = datetime.time(20,15)
        event_occurrence.time_ended = datetime.time(22,15)
        event_occurrence.number_of_teams = 5
        self.assertTrue(event_occurrence.is_complete)

    def test_is_complete_game_with_incomplete_data_is_false(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        event_occurrence.status = 'Game'
        event_occurrence.time_started = datetime.time(20,15)
        self.assertFalse(event_occurrence.is_complete)

    def test_is_complete_no_game_with_complete_data_is_true(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        event_occurrence.status = 'No Game'
        event_occurrence.cancellation_reason = 'Holiday'
        self.assertTrue(event_occurrence.is_complete)

    def test_is_complete_no_game_with_incomplete_data_is_false(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        event_occurrence.status = 'No Game'
        self.assertFalse(event_occurrence.is_complete)
        
    def test_has_passed_true(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        second_before_now = (datetime.datetime.now() - datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_before_now)
        event_occurrence.time = time
        event_occurrence.date = datetime.date.today()
        self.assertTrue(event_occurrence.has_passed)
        
    def test_has_passed_false(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)
        event_occurrence.time = time
        event_occurrence.date = datetime.date.today()
        self.assertFalse(event_occurrence.has_passed)
        
    def test_can_be_edited_true_game(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)
        event_occurrence.time = time
        event_occurrence.status = 'Game'
        event_occurrence.time_started = datetime.time(20,15)
        event_occurrence.time_ended = datetime.time(22,15)
        event_occurrence.number_of_teams = 5
        self.assertTrue(event_occurrence.can_be_edited)
        
    def test_can_be_edited_true_no_game(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        second_after_now = (datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)
        event_occurrence.time = time
        event_occurrence.status = 'No Game'
        event_occurrence.cancellation_reason = 'Emergency'
        self.assertTrue(event_occurrence.can_be_edited)
        
    def test_can_be_edited_false_game(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        second_after_now = (
            datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)
        event_occurrence.time = time
        event_occurrence.status = 'Game'
        self.assertFalse(event_occurrence.can_be_edited)
        
    def test_can_be_edited_false_no_game(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        second_after_now = (
            datetime.datetime.now() + datetime.timedelta(seconds=1)).time()
        time = Time.objects.create(time=second_after_now)
        event_occurrence.time = time
        event_occurrence.status = 'No Game'
        self.assertFalse(event_occurrence.can_be_edited)

    def test_is_late_true(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        two_days_and_one_second_before_now = (
            datetime.datetime.now() - datetime.timedelta(days=2, seconds=1))
        event_occurrence.date = two_days_and_one_second_before_now
        time = Time.objects.create(
            time=two_days_and_one_second_before_now.time())
        event_occurrence.time = time
        event_occurrence.status = 'Game'
        self.assertTrue(event_occurrence.is_late)
        
    def test_is_late_false(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        within_two_hours_passed = (
            datetime.datetime.now() - datetime.timedelta(days=1, hours=23, minutes=59, seconds=59))
        event_occurrence.date = within_two_hours_passed
        time = Time.objects.create(
            time=within_two_hours_passed.time())
        event_occurrence.time = time
        event_occurrence.status = 'Game'
        self.assertFalse(event_occurrence.is_late)

    def test_display_game_length_no_value(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        event_occurrence.status = 'Game'
        self.assertEqual(str(event_occurrence.display_game_length()), 'Not applicable')
        
    def test_display_game_length_with_start_and_end_values(self):
        event_occurrence = EventOccurrence.objects.get(pk=1)
        event_occurrence.status = 'Game'
        event_occurrence.time_started = datetime.time(20,15)
        event_occurrence.time_ended = datetime.time(22,15)
        self.assertEqual(str(event_occurrence.display_game_length()), '2:00:00')
        
    def test_clean_date_and_day_of_the_week_do_not_coincide_validation_error(self):
        day = Day.objects.get(pk=1)
        with self.assertRaises(ValidationError) as cm:
            event_occurrence = EventOccurrence(
                day=day,
                date=datetime.date(year=2019, month=5, day=13))
            event_occurrence.full_clean()
        exception = cm.exception
        self.assertEqual(
            exception.messages,
            ['The date and day of the week do not coincide. '
            'Did you mean Mon?'])
            
    def test_clean_cancelled_ahead_with_no_reason_validation_error(self):
        with self.assertRaises(ValidationError) as cm:
            event_occurrence = EventOccurrence.objects.get(pk=1)
            event_occurrence.cancelled_ahead = True
            event_occurrence.full_clean()
        exception = cm.exception
        self.assertEqual(
            exception.messages,
            ['Please put a reason for cancelling ahead.'])
            
    def test_clean_no_game_with_no_reason_validation_error(self):
        with self.assertRaises(ValidationError) as cm:
            event_occurrence = EventOccurrence(status='No Game')
            event_occurrence.full_clean()
        exception = cm.exception
        self.assertEqual(
            exception.messages,
            ['Please put a reason for cancelling.'])
            
    def test_clean_game_with_cancellation_reason(self):
        with self.assertRaises(ValidationError) as cm:
            event_occurrence = EventOccurrence(
                status='Game', cancellation_reason='Holiday')
            event_occurrence.full_clean()
        exception = cm.exception
        self.assertEqual(
            exception.messages,
            ['You have a cancellation reason when there '
            'was a game. Please correct.'])