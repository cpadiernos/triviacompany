import calendar
import datetime
from django.conf import settings
import os

from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext as _

from locations.models import Venue

from PIL import Image, ExifTags
from io import BytesIO

from django.conf import settings

class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
            for event_image in EventImage.objects.filter(image=name.replace('\\','/')):
                event_image.delete()
        return name

def image_path(instance, filename):
    folder = 'event_images'
    sub_folder = str(instance.event.venue.name).replace(" ", "_").replace("\'", "").lower()
    return '{0}/{1}/{2}'.format(folder, sub_folder, filename)

def scoresheet_path(instance, filename):
    folder = 'scoresheets'
    sub_folder = str(instance.event.venue.name).replace(" ", "_").replace("\'", "").lower()
    event_occurrence_date = instance.date
    return '{0}/{1}/{2}_{3}'.format(folder, sub_folder, event_occurrence_date, filename)

def compare_day_and_date(self, day, date, name):
    try:
        if day.day is not date.weekday():
            raise ValidationError(
                _('The ' + name +' and day of the week do not coincide. '
                'Did you mean %(day)s?'),
                code='invalid',
                params={'day': calendar.day_abbr[date.weekday()]})
    except AttributeError:
        raise ValidationError(
            _('Please specify the day of the week.'), code='invalid')

class Day(models.Model):

    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6
    DAY = (
        (MON, 'Mon'),
        (TUE, 'Tue'),
        (WED, 'Wed'),
        (THU, 'Thu'),
        (FRI, 'Fri'),
        (SAT, 'Sat'),
        (SUN, 'Sun'),
    )

    day = models.IntegerField(choices=DAY, primary_key=True)

    class Meta:
        #db_table = 'day'
        ordering = ['day']

    def __str__(self):
        return calendar.day_abbr[self.day]

class Time(models.Model):
    DEFAULT_TIME = datetime.time(20,0)
    time = models.TimeField(default=DEFAULT_TIME, primary_key=True)

    class Meta:
        #db_table = 'time'
        ordering = ['time']

    def __str__(self):
        return self.time.strftime('%I:%M %p')

class Event(models.Model):
    venue = models.ForeignKey(
        Venue, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='events')
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,on_delete=models.SET_NULL, null=True,
        blank=True, related_name='events')
    day = models.ForeignKey(
        Day, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='events')
    time = models.ForeignKey(
        Time, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='events')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    first_place_prize = models.CharField(max_length=50, blank=True)
    second_place_prize = models.CharField(max_length=50, blank=True)
    third_place_prize = models.CharField(max_length=50, blank=True)
    additional_prize_info = models.TextField(blank=True)

    EVENT_STATUS = (
        ('S','Starting'),
        ('A','Active'),
        ('E','Ending'),
        ('T','Terminated'),
    )

    status = models.CharField(max_length=1, choices=EVENT_STATUS, blank=True)
    request_future_restart = models.BooleanField(default=False)

    BASE_TEAMS = 5
    BASE_RATE = 125
    INCREMENTAL_TEAMS = 1
    INCREMENTAL_RATE = 5

    base_teams = models.PositiveSmallIntegerField(
        default=BASE_TEAMS, null=True, blank=True)
    base_rate = models.DecimalField(
        max_digits=6, decimal_places=2,
        default=BASE_RATE, null=True, blank=True)
    incremental_teams = models.PositiveSmallIntegerField(
        default=INCREMENTAL_TEAMS, null=True, blank=True)
    incremental_rate = models.DecimalField(
        max_digits=6, decimal_places=2,
        default=INCREMENTAL_RATE, null=True, blank=True)

    # class Meta:
        # db_table = 'event'

    def __str__(self):
        return '{0} ({1} at {2})'.format(
            self.venue, self.day, self.time)

    def get_absolute_url(self):
        return reverse('event-detail', args=[self.pk])

    def clean(self):
        if self.start_date:
            compare_day_and_date(self, self.day, self.start_date, 'start date')

        if self.end_date:
            compare_day_and_date(self, self.day, self.end_date, 'end date')

        if self.start_date and self.end_date:
                if self.end_date < self.start_date:
                    raise ValidationError(
                        _('The start date is later than the end date. '
                        'Please correct.'), code='invalid')

        margin = datetime.timedelta(days = 14)
        if self.start_date and self.start_date > datetime.date.today():
            self.status = 'S'
        elif self.end_date and self.end_date < datetime.date.today():
            self.status = 'T'
        elif self.end_date and self.end_date < datetime.date.today() + margin:
            self.status = 'E'
        elif self.start_date and self.start_date < datetime.date.today():
            self.status = 'A'

class EventImage(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='images')
    image = models.ImageField(
        upload_to=image_path, blank=True, storage=OverwriteStorage())

    # class Meta:
        # db_table = 'event_image'

    def __str__(self):
        return '{0}'.format(self.event)

    def save(self, *args, **kwargs):
        if self.image:
            imagetemp = Image.open(BytesIO(self.image.read()))
            for code, description in ExifTags.TAGS.items():
                if description == 'Orientation':
                    break

            if imagetemp._getexif():
                exif = imagetemp._getexif()
                if code in exif:
                    if exif[code] == 3:
                        imagetemp = imagetemp.rotate(180, expand=True)
                    elif exif[code] == 6:
                        imagetemp = imagetemp.rotate(270, expand=True)
                    elif exif[code] == 8:
                        imagetemp = imagetemp.rotate(90, expand=True)

            outputstream = BytesIO()
            imagetemp.thumbnail((500,500), Image.ANTIALIAS)
            imagetemp.save(outputstream, format='JPEG', quality=75)
            outputstream.seek(0)
            self.image = File(outputstream, self.image.name)
        super().save(*args, **kwargs)

class EventOccurrence(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='event_occurrences')
    day = models.ForeignKey(
        Day, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='event_occurrences')
    time = models.ForeignKey(
        Time, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='event_occurrences')
    date = models.DateField(null=True, blank=True)
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='event_occurrences')
    change_host = models.BooleanField('change host', default=False)

    EVENT_OCCURRENCE_STATUS = (
        ('Game','Game'),
        ('No Game','No Game'),
    )
    status = models.CharField(
        max_length=7, default='Game',
        choices=EVENT_OCCURRENCE_STATUS, blank=False)

    REASON = (
        ('Low/No Attendance','Low or No Attendance'),
        ('Alternate Event', 'Alternate Event'),
        ('Holiday', 'Holiday'),
        ('Inclement Weather', 'Inclement Weather'),
        ('Renovations', 'Renovations'),
        ('Emergency', 'Emergency'),
        ('Other', 'Other'),
    )

    cancellation_reason = models.CharField(
        max_length=20, choices=REASON, blank=True,
        help_text='Only required if "No Game" was chosen.')
    cancelled_ahead = models.BooleanField('cancelled ahead', default=False)
    time_started = models.TimeField(
        null=True, blank=True,
        help_text='ex. 08:10 PM. Only required if "Game" was chosen.')
    time_ended = models.TimeField(
        null=True, blank=True,
        help_text='ex. 10:05 PM. Only required if "Game" was chosen.')
    number_of_teams = models.PositiveIntegerField(
        null=True, blank=True, help_text='Only required if "Game" was chosen.')
    scoresheet = models.FileField(
        upload_to=scoresheet_path, blank=True, storage=OverwriteStorage())
    notes = models.TextField(
        blank=True,
        help_text=('Please include notes about the game here. '
                  'For example, technical problems, '
                  'customer issues, suggestions, etc...'))

    class Meta:
        # db_table = 'event_occurrence'
        ordering = ('date', 'time')

    def __str__(self):
        return '{0} - {1} ({2})'.format(self.event, self.date, self.host)

    @property
    def is_different_time(self):
        return self.time != self.event.time

    @property
    def is_different_day(self):
        return self.day != self.event.day

    @property
    def is_different_host(self):
        return self.event.host != self.host

    @property
    def is_complete(self):
        if self.status == 'Game' and self.time_started and self.time_ended:
            return True
        elif self.status == 'No Game' and self.cancellation_reason:
            return True
        else:
            return False

    @property
    def has_passed(self):
        return(datetime.datetime.combine(self.date, self.time.time)
            < datetime.datetime.now())

    @property
    def can_be_edited(self):
        return self.has_passed and self.is_complete

    @property
    def is_late(self):
        if not self.is_complete and (
            (datetime.datetime.combine(self.date, self.time.time)
            + datetime.timedelta(days=2)) < datetime.datetime.now()):
            return True
        else:
            return False

    def display_game_length(self):
        if self.time_started and self.time_ended:
            return (datetime.datetime.combine(
                datetime.datetime(1,1,1,0,0,0), self.time_ended)
                - datetime.datetime.combine(
                datetime.datetime(1,1,1,0,0,0), self.time_started))
        else:
            return 'Not applicable'
    display_game_length.short_description = 'Game Length'

    def clean(self):
        if self.date:
            compare_day_and_date(self, self.day, self.date, 'date')
        if self.cancelled_ahead and not self.cancellation_reason:
            raise ValidationError(
                _('Please put a reason for cancelling ahead.'),
                code='invalid')
        if self.status == 'No Game' and not self.cancellation_reason:
            raise ValidationError(
                _('Please put a reason for cancelling.'),
                code='invalid')
        if self.status == 'Game' and self.cancellation_reason:
            raise ValidationError(
                _('You have a cancellation reason when there was a game. '
                'Please correct.'), code='invalid')
