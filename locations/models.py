from django.conf import settings
from django.db import models

from localflavor.us.models import USStateField, USZipCodeField
from localflavor.us.us_states import US_STATES
from phone_field import PhoneField

#from .utils import find_region
from .utils import google_map_address

class Region(models.Model):
    name = models.CharField(max_length=10, primary_key=True, blank=False)
    
    class Meta:
        #db_table = 'region'
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        self.name = self.name.upper()

class State(models.Model):
    name = USStateField(choices=US_STATES, primary_key=True, blank=False)
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='states')

    class Meta:
        #db_table = 'state'
        ordering = ['name']

    def __str__(self):
        return self.name
        
    # def clean(self):
        # region_name = find_region(self.get_name_display())
        # region, created = Region.objects.get_or_create(name=region_name)
        # self.region = region
        
class City(models.Model):
    name = models.CharField(max_length=100, blank=False)
    state = models.ForeignKey(
        State, on_delete=models.SET_NULL, null=True,
        blank=False, related_name='cities')

    class Meta:
        #db_table = 'city'
        verbose_name_plural = 'cities'
        ordering = ['name']
        unique_together = ('name', 'state')

    def __str__(self):
        return '{0}, {1}'.format(self.name, self.state)

class Zip(models.Model):
    code = USZipCodeField(blank=False)
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True,
        blank=False, related_name='zips')

    class Meta:
        #db_table = 'zip'
        unique_together = ('code', 'city')

    def __str__(self):
        return self.code
        
class Venue(models.Model):
    name = models.CharField(max_length=200, blank=True)
    address = models.CharField(max_length=200, blank=True)
    additional_address = models.CharField(max_length=200, blank=True)
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='venues')
    state = models.ForeignKey(
        State, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='venues')
    zip = models.ForeignKey(
        Zip, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='venues')
    email = models.EmailField(max_length=200, blank=True)
    phone_number = PhoneField(blank=True)
    website = models.CharField(max_length=200, blank=True)
    av_setup = models.TextField(blank=True)
    managers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, through='ManagementPeriod')

    class Meta:
        #db_table = 'venue'
        ordering = ['name']

    def __str__(self):
        return self.name

    def display_manager(self):
        return ', '.join(
            [ manager.username for manager in self.managers.all() ])
    display_manager.short_description = 'Manager(s)'
    
    def map_link(self):
        return google_map_address(self)

class ManagementPeriod(models.Model):
    venue = models.ForeignKey(
        Venue, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='management_periods')
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='management_periods')
    date_started = models.DateField(null=True, blank=True)
    date_ended = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        #db_table = 'management_period'
        ordering = ('venue', 'manager')

    def __str__(self):
        return '{0} at {1}'.format(self.manager, self.venue)