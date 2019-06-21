from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils.translation import ugettext as _

from locations.models import Region, State, City, Zip
from locations.utils import google_map_address

from phone_field import PhoneField

class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name

class CustomUser(AbstractUser):
    is_regional_manager = models.BooleanField('RM', default=False)
    is_host = models.BooleanField('host', default=False)
    is_venue_manager = models.BooleanField('VM', default=False)

    secondary_email = models.EmailField(max_length=200, blank=True)

    mobile_number = PhoneField(max_length=12, blank=True)
    work_number = PhoneField(max_length=12, blank=True)

    mailing_address = models.CharField(max_length=200, blank=True)
    mailing_additional_address = models.CharField(max_length=100, blank=True)
    mailing_city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='users')
    mailing_state = models.ForeignKey(
        State, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='users')
    mailing_zip = models.ForeignKey(
        Zip, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='users')

    profile_image = models.ImageField(
        upload_to='profile_images', blank=True, storage=OverwriteStorage())

    def clean(self):
        if (self.is_regional_manager is False
            and self.is_host is False
            and self.is_venue_manager is False):
            raise ValidationError(_('Please assign a role.'), code='required')

class HostProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        blank=True, related_name='host_profile')
    bio = models.TextField(blank=True)

    has_event = models.BooleanField('has event', default=True)

    residential_address = models.CharField(
        max_length=200, blank=True)
    residential_additional_address = models.CharField(
        max_length=100, blank=True)
    residential_city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='host_profiles')
    residential_state = models.ForeignKey(
        State, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='host_profiles')
    residential_zip = models.ForeignKey(
        Zip, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='host_profiles')

    BASE_TEAMS = 5
    BASE_RATE = 50
    INCREMENTAL_TEAMS = 1
    INCREMENTAL_RATE = 2

    base_teams = models.DecimalField(
        max_digits=5, decimal_places=2, null=True,
        blank=True, default=BASE_TEAMS)
    base_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True,
        blank=True, default=BASE_RATE)
    incremental_teams = models.DecimalField(
        max_digits=5, decimal_places=2, null=True,
        blank=True, default=INCREMENTAL_TEAMS)
    incremental_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True,
        blank=True, default=INCREMENTAL_RATE)

    def __str__(self):
        return self.user.username

    def map_link(self):
        return google_map_address(self)

class RegionalManagerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        blank=True, related_name='regional_manager_profile')
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='regional_manager_profiles')
    weekly_pay = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.user.username

class VenueManagerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        blank=True, related_name='venue_manager_profile')

    COMMUNICATION = [
        ('Cell', 'Cellphone'),
        ('Venue', 'Venue phone'),
        ('Email', 'Email')
    ]

    best_reached_by = models.CharField(
        max_length=5, choices=COMMUNICATION, blank=True)

    def __str__(self):
        return self.user.username

    def display_preferred_communication(self):
        if self.best_reached_by == 'Cell':
            return self.user.mobile_number
        elif self.best_reached_by == 'Venue':
            return self.user.work_number
        else:
            return self.user.email
    display_preferred_communication.short_description = 'Number or Email'