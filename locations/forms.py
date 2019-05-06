from django import forms
from .models import Venue, State, City, Zip
from localflavor.us.forms import USStateField, USZipCodeField
from localflavor.us.us_states import US_STATES

class VenueForm(forms.ModelForm):
    STATE_CHOICES = list(US_STATES)
    STATE_CHOICES.insert(0, ('', '---------'))
    
    city = forms.CharField(max_length=200, required=True)
    state = forms.CharField(
        widget=forms.Select(choices=STATE_CHOICES), required=True)
    zip = USZipCodeField(required=True)

    field_order = [
        'name', 'address', 'additional_address',
        'city', 'state', 'zip',
        'email', 'phone_number', 'website', 'av_setup',
        'managers',
    ]
    
    required_fields = ('name', 'address')
    
    class Meta:
        model = Venue
        fields = (
            'name', 'address', 'additional_address',
            'email', 'phone_number', 'website', 'av_setup',
            'managers',
        )
        
    def clean(self):
        super().clean()
        city_name = self.cleaned_data.get('city')
        state_name = self.cleaned_data.get('state')
        zip_code = self.cleaned_data.get('zip')
        if city_name is not None and state_name is not None and zip_code is not None:
            state, created = State.objects.get_or_create(name=state_name)
            city, created = City.objects.get_or_create(name=city_name, state=state)
            zip, created = Zip.objects.get_or_create(code=zip_code, city=city)
            self.cleaned_data['city'] = city
            self.cleaned_data['state'] = state
            self.cleaned_data['zip'] = zip
        return self.cleaned_data
     
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in self.required_fields:
            self.fields[key].required = True 