import datetime

from django.forms.widgets import HiddenInput
from django.test import TestCase

from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse

from accounts.models import CustomUser
from locations.models import Venue
from schedule.models import Day, Time, Event, EventOccurrence
from schedule.forms import EventOccurrenceForm, ChangeHostForm

class EventOccurrenceFormTests(TestCase):

    def test_event_occurrence_form__meta(self):
        self.assertEqual(EventOccurrence, EventOccurrenceForm.Meta.model)
        self.assertEqual(('status', 'cancellation_reason', 'time_started', 'time_ended',
            'number_of_teams', 'scoresheet', 'notes'), EventOccurrenceForm.Meta.fields)
        
    def test_event_occurrence_form_valid_post_data_no_game(self):
        form = EventOccurrenceForm({
            'status': 'No Game',
            'cancellation_reason': 'Alternate Event'
        })
        self.assertTrue(form.is_valid())
        
    def test_event_occurrence_form_invalid_post_data_no_game(self):
        form = EventOccurrenceForm({
            'status': 'No Game',
            'cancellation_reason': ''
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['cancellation_reason'], ['This field is required.'])
        
    def test_event_occurrence_form_valid_post_data_game(self):
        test_file = SimpleUploadedFile('scoresheet.txt', b'Team Spaghetti 100 points')
        data = {
            'status': 'Game',
            'time_started': '08:00 PM',
            'time_ended': '10:00 PM',
            'number_of_teams': 5,
        }
        files = {
            'scoresheet': test_file,
        }
        form = EventOccurrenceForm(data, files)
        self.assertTrue(form.is_valid())
        
    def test_event_occurrence_form_invalid_post_data_game(self):
        data = {
            'status': 'Game',
            'time_started': '',
            'time_ended': '',
            'number_of_teams': '',
        }
        files = {
            'scoresheet': '',
        }
        form = EventOccurrenceForm(data, files)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['time_started'], ['This field is required.'])
        self.assertEqual(
            form.errors['time_ended'], ['This field is required.'])
        self.assertEqual(
            form.errors['number_of_teams'], ['This field is required.'])
        self.assertEqual(
            form.errors['scoresheet'], ['This field is required.'])
            
    def test_event_occurrence_form_game_clean_clears_up_cancellation_reason(self):
        test_file = SimpleUploadedFile('scoresheet.txt', b'Team Spaghetti 100 points')
        data = {
            'status': 'Game',
            'cancellation_reason': 'Holiday',
            'time_started': '08:00 PM',
            'time_ended': '10:00 PM',
            'number_of_teams': 5,
        }
        files = {
            'scoresheet': test_file,
        }
        form = EventOccurrenceForm(data, files)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.cancellation_reason, '')
        
    def test_event_occurrence_form_no_game_clean_clears_up_game_fields(self):
        test_file = SimpleUploadedFile('scoresheet.txt', b'Team Spaghetti 100 points')
        data = {
            'status': 'No Game',
            'cancellation_reason': 'Holiday',
            'time_started': '08:00 PM',
            'time_ended': '10:00 PM',
            'number_of_teams': 5,
        }
        files = {
            'scoresheet': test_file,
        }
        form = EventOccurrenceForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.time_started, None)
        self.assertEqual(form.instance.time_ended, None)
        self.assertEqual(form.instance.number_of_teams, None)
        self.assertEqual(bool(form.instance.scoresheet), False)
        
    def test_event_occurrence_form_game_with_greater_than_three_hour_time_length_returns_error(self):
        test_file = SimpleUploadedFile('scoresheet.txt', b'Team Spaghetti 100 points')
        data = {
            'status': 'Game',
            'time_started': '07:00 PM',
            'time_ended': '10:01 PM',
            'number_of_teams': 5,
        }
        files = {
            'scoresheet': test_file,
        }
        form = EventOccurrenceForm(data, files)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['__all__'], ['The duration of the game should be around 2 hours. '
                        'Double check your inputted time.'])
                        
    def test_event_occurrence_form_game_with_end_time_earlier_than_start_time_returns_error(self):
        test_file = SimpleUploadedFile('scoresheet.txt', b'Team Spaghetti 100 points')
        data = {
            'status': 'Game',
            'time_started': '07:00 PM',
            'time_ended': '06:59 PM',
            'number_of_teams': 5,
        }
        files = {
            'scoresheet': test_file,
        }
        form = EventOccurrenceForm(data, files)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['__all__'], ['The duration of the game should be around 2 hours. '
                        'Double check your inputted time.'])
                        
    def test_event_occurrence_form_game_with_valid_late_start_into_next_day_does_not_return_error(self):
        test_file = SimpleUploadedFile('scoresheet.txt', b'Team Spaghetti 100 points')
        data = {
            'status': 'Game',
            'time_started': '10:00 PM',
            'time_ended': '01:00 AM',
            'number_of_teams': 5,
        }
        files = {
            'scoresheet': test_file,
        }
        form = EventOccurrenceForm(data, files)
        self.assertTrue(form.is_valid())
        
    def test_event_occurrence_form_game_with_late_start_into_next_day_longer_than_three_hours_returns_error(self):
        test_file = SimpleUploadedFile('scoresheet.txt', b'Team Spaghetti 100 points')
        data = {
            'status': 'Game',
            'time_started': '10:00 PM',
            'time_ended': '01:01 AM',
            'number_of_teams': 5,
        }
        files = {
            'scoresheet': test_file,
        }
        form = EventOccurrenceForm(data, files)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['__all__'], ['The duration of the game should be around 2 hours. '
                        'Double check your inputted time.'])

class ChangeHostFormTests(TestCase):

    def test_change_host_form__meta(self):
        self.assertEqual(EventOccurrence, ChangeHostForm.Meta.model)
        self.assertEqual(['change_host'], ChangeHostForm.Meta.fields)
        
    def test_change_host_form_has_hidden_change_host_field(self):
        form = ChangeHostForm()
        for field in form:
            self.assertIsInstance(field.field.widget, HiddenInput)