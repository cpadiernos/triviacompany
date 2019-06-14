import datetime

from django import forms
from django.utils.translation import ugettext as _

from .models import EventOccurrence

class EventOccurrenceForm(forms.ModelForm):

    class Meta:
        model = EventOccurrence
        fields = (
            'status', 'cancellation_reason',
            'time_started', 'time_ended',
            'number_of_teams', 'scoresheet', 'notes')

    def fields_required(self, fields):
        for field in fields:
            if not self.cleaned_data.get(field, ''):
                msg = forms.ValidationError(
                    _('This field is required.'), code='required')
                self.add_error(field, msg)

    def clean(self):
        super().clean()
        status = self.cleaned_data.get('status')

        if status == 'Game':
            self.fields_required(['time_started'])
            self.fields_required(['time_ended'])
            self.fields_required(['number_of_teams'])
            self.fields_required(['scoresheet'])
        else:
            self.cleaned_data['time_started'] = None
            self.cleaned_data['time_ended'] = None
            self.cleaned_data['number_of_teams'] = None
            scoresheet = self.cleaned_data['scoresheet']
            if bool(scoresheet) == True:
                scoresheet.name = None

        if status == 'No Game':
            self.fields_required(['cancellation_reason'])
        else:
            self.cleaned_data['cancellation_reason'] = ''

        if ('time_started' in self.cleaned_data
            and 'time_ended' in self.cleaned_data):
            if (self.cleaned_data['time_started']
                and self.cleaned_data['time_ended']):
                duration = (datetime.datetime.combine(
                    datetime.datetime(1,1,1,0,0,0),
                    self.cleaned_data['time_ended'])
                    - datetime.datetime.combine(
                    datetime.datetime(1,1,1,0,0,0),
                    self.cleaned_data['time_started']))
                if duration > datetime.timedelta(hours=3):
                    raise forms.ValidationError(
                        _('The duration of the game should be around 2 hours. '
                        'Double check your inputted time.'), code='invalid')
                if (duration > datetime.timedelta(days=-1, hours=3)
                    and duration < datetime.timedelta(days=0)):
                    raise forms.ValidationError(
                        _('The duration of the game should be around 2 hours. '
                        'Double check your inputted time.'), code='invalid')
        return self.cleaned_data

class ChangeHostForm(forms.ModelForm):

    class Meta:
        model = EventOccurrence
        fields = ['change_host']

        widgets = {'change_host': forms.HiddenInput()}