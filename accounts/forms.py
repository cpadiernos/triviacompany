from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'is_regional_manager', 'is_host', 'is_venue_manager',
            'secondary_email', 'mobile_number', 'work_number',
            'mailing_address', 'mailing_additional_address',
            'mailing_city', 'mailing_state', 'mailing_zip',
            'profile_image')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = (
            'is_regional_manager', 'is_host', 'is_venue_manager',
            'secondary_email', 'mobile_number', 'work_number',
            'mailing_address', 'mailing_additional_address',
            'mailing_city', 'mailing_state', 'mailing_zip',
            'profile_image')