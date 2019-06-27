import datetime

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView

from .filters import VenueFilter
from .forms import VenueForm
from .models import Venue, City

class VenueListView(generic.ListView):
    model = Venue
    context_object_name = 'venue_list'
    template_name = 'locations/venue_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        venues = Venue.objects.all()
        context['count'] = venues.count()
        context['filter'] = VenueFilter(self.request.GET, queryset=venues)
        return context
        
class VenueCreate(CreateView):
    form_class = VenueForm
    template_name = 'locations/venue_form.html'
    success_url = reverse_lazy('venue-list')
    
    def form_valid(self, form):
        form.instance.city = form.cleaned_data['city']
        form.instance.state = form.cleaned_data['state']
        form.instance.zip = form.cleaned_data['zip']
        return super().form_valid(form)
        
class VenueUpdate(UpdateView):
    model = Venue
    form_class = VenueForm
    template_name = 'locations/venue_form.html'
    success_url = reverse_lazy('venue-list')
    
    def get_initial(self):
        pk = self.kwargs['pk']
        venue = Venue.objects.get(pk=pk)
        city = venue.city.name
        state = venue.state
        zip = venue.zip
        return {'city': city, 'state': state, 'zip': zip}
        
    def form_valid(self, form):
        form.instance.city = form.cleaned_data['city']
        form.instance.state = form.cleaned_data['state']
        form.instance.zip = form.cleaned_data['zip']
        return super().form_valid(form)
        
def load_cities(request):
    state_id = request.GET.get('state')
    if state_id:
        cities = City.objects.filter(state_id=state_id).order_by('name')
    else:
        cities = City.objects.filter(
            venues__events__event_occurrences__isnull=False,
            venues__events__event_occurrences__date__gte=datetime.date.today()).distinct()
    return render(request, 'locations/city_dropdown_list.html', {'cities': cities})