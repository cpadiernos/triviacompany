import django_filters
from django import forms
from .models import City, State, Venue

class VenueFilter(django_filters.FilterSet):
    state = django_filters.ModelChoiceFilter(
        queryset=State.objects.all(), widget=forms.Select(),
        label='State', empty_label='All')
    city = django_filters.ModelChoiceFilter(
        queryset=City.objects.all(), label='City')
        
    class Meta:
        model = Venue
        fields = ('state', 'city')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        state_pks = self.queryset.values_list('state', flat=True)
        city_pks = self.queryset.values_list('city', flat=True)
        self.filters['state'].field.queryset = State.objects.filter(pk__in=state_pks)
        self.filters['city'].field.queryset = City.objects.filter(pk__in=city_pks)