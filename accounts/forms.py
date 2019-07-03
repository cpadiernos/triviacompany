from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext as _

from .models import CustomUser
from locations.models import City, State, Zip

from localflavor.us.forms import USStateField, USZipCodeField
from localflavor.us.us_states import US_STATES

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

class CustomUserUpdateForm(forms.ModelForm):
    STATE_CHOICES = list(US_STATES)
    STATE_CHOICES.insert(0, ('', '---------'))

    mailing_city = forms.CharField(max_length=200, required=False)
    mailing_state = USStateField(widget=forms.Select(choices=STATE_CHOICES), required=False)
    mailing_zip = USZipCodeField(required=False)

    class Meta:
        model = CustomUser
        fields = (
            'first_name', 'last_name',
            'email', 'secondary_email',
            'mobile_number', 'work_number',
            'mailing_address', 'mailing_additional_address',
            'mailing_city', 'mailing_state', 'mailing_zip',
            'profile_image'
        )
        widgets = {
            'profile_image': forms.FileInput(),
            }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        username = self.request.user.username
        user = CustomUser.objects.get(username=username)
        mailing_city = getattr(user.mailing_city, 'name', '')
        mailing_state = getattr(user.mailing_state, 'name', '')
        mailing_zip = getattr(user.mailing_zip, 'code', '')
        kwargs['initial']['mailing_city'] = mailing_city
        kwargs['initial']['mailing_state'] = mailing_state
        kwargs['initial']['mailing_zip'] = mailing_zip
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        required_together = ['mailing_address', 'mailing_state', 'mailing_city', 'mailing_zip']
        input = {field:self.cleaned_data.get(field) for field in required_together}
        if all(input.values()):
            state, created = State.objects.get_or_create(name=input.get('mailing_state'))
            city, created = City.objects.get_or_create(name=input.get('mailing_city'), state=state)
            zip, created = Zip.objects.get_or_create(code=input.get('mailing_zip'), city=city)
            self.cleaned_data['mailing_state'] = state
            self.cleaned_data['mailing_city'] = city
            self.cleaned_data['mailing_zip'] = zip
        elif any(input.values()):
            message = 'Please provide the full address.'
            error = forms.ValidationError(_(message), code='required')
            for field in required_together:
                self.add_error(field, error)
            raise forms.ValidationError(_('Please correct the error below.'), code='invalid')
        else:
            self.cleaned_data['mailing_state'] = None
            self.cleaned_data['mailing_city'] = None
            self.cleaned_data['mailing_zip'] = None
