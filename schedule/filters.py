import django_filters
from django import forms

from .models import Day, EventOccurrence

from locations.models import City, State

class EventOccurrenceFilter(django_filters.FilterSet):
    event__venue__state = django_filters.ModelChoiceFilter(
        queryset=State.objects.all(), widget=forms.Select(),
        label='State', empty_label='All')
    event__venue__city = django_filters.ModelChoiceFilter(
        queryset=City.objects.all(), label='City')

    class Meta:
        model = EventOccurrence
        fields = ['event__venue__state', 'event__venue__city', 'day']

    def narrow_choices(self, field, model):
        pks = self.queryset.values_list(field, flat=True)
        self.filters[field].field.queryset = model.objects.filter(pk__in=pks)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.narrow_choices('event__venue__state', State)
        self.narrow_choices('event__venue__city', City)
        self.narrow_choices('day', Day)
