import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.views.generic.edit import UpdateView
from django.urls import reverse

from .filters import EventOccurrenceFilter
from .forms import ChangeHostForm, EventOccurrenceForm
from .models import Event, EventOccurrence, Day

class EventDetailView(generic.DetailView):
    model = Event
    context_object_name = 'event'
    template_name = 'schedule/event_detail.html'
    
class EventOccurrenceListView(generic.ListView):
    model = EventOccurrence
    context_object_name = 'event_occurrence_list'
    template_name = 'schedule/event_occurrence_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.datetime.now()
        event_occurrence_list_future = EventOccurrence.objects.filter(
            date__gte=now).order_by('date')
        event_occurrence_filter = EventOccurrenceFilter(
            self.request.GET, queryset=event_occurrence_list_future)
        context['filter'] = event_occurrence_filter
        return context
    
class EventOccurrenceListViewPast(EventOccurrenceListView):

    def get_queryset(self):
        now = datetime.datetime.now()
        event_occurrence_list = EventOccurrence.objects.filter(
            date__lte=now).order_by('-date')
        return event_occurrence_list
        
class EventOccurrenceListViewFuture(EventOccurrenceListView):

    def get_queryset(self):
        now = datetime.datetime.now()
        event_occurrence_list = EventOccurrence.objects.filter(
            date__gte=now).order_by('date')
        return event_occurrence_list
        
class EventOccurrenceListViewAvailable(LoginRequiredMixin, EventOccurrenceListView):

    def get_queryset(self):
        now = datetime.datetime.now()
        event_occurrence_list = EventOccurrence.objects.filter(
            change_host=True, date__gte=now).order_by('date')
        return event_occurrence_list

class EventOccurrenceListViewHost(LoginRequiredMixin, EventOccurrenceListView):
        
    def get_queryset(self):
        event_occurrence_list = super().get_queryset()
        if self.kwargs['username'] == self.request.user.username:
            event_occurrence_list_host = event_occurrence_list.filter(
                Q(event__host=self.request.user)| Q(host=self.request.user))
            return event_occurrence_list_host
        else:
            raise Http404
        
class EventOccurrenceListViewPastHost(LoginRequiredMixin, EventOccurrenceListViewPast):

    def get_queryset(self):
        event_occurrence_list = super().get_queryset()
        if self.kwargs['username'] == self.request.user.username:
            event_occurrence_list_host = event_occurrence_list.filter(
                Q(event__host=self.request.user)| Q(host=self.request.user))
            return event_occurrence_list_host
        else:
            raise Http404
        
class EventOccurrenceListViewFutureHost(LoginRequiredMixin, EventOccurrenceListViewFuture):

    def get_queryset(self):
        event_occurrence_list = super().get_queryset()
        if self.kwargs['username'] == self.request.user.username:
            event_occurrence_list_host = event_occurrence_list.filter(
                Q(event__host=self.request.user)| Q(host=self.request.user))
            return event_occurrence_list_host
        else:
            raise Http404
        
class EventOccurrenceUpdate(LoginRequiredMixin, UpdateView):
    model = EventOccurrence
    form_class = EventOccurrenceForm
    template_name = 'schedule/event_occurrence_form.html'

    def get_object(self, queryset=None):
        event_occurrence_pk = self.kwargs['pk']
        event_occurrence = get_object_or_404(
            EventOccurrence, pk=event_occurrence_pk)
        if (event_occurrence.host == self.request.user 
                and event_occurrence.has_passed
                and not event_occurrence.cancelled_ahead):
            return event_occurrence
        else:
            raise Http404
            
    def get_success_url(self):
        return reverse(
            'event-occurrence-list-host',
            kwargs={'username': self.request.user.username })

class RequestOff(LoginRequiredMixin, UpdateView):
    model = EventOccurrence
    context_object_name = 'event_occurrence'
    form_class = ChangeHostForm
    template_name = 'schedule/change_host_form.html'

    def get_object(self, queryset=None):
        event_occurrence_pk = self.kwargs['pk']
        event_occurrence = get_object_or_404(
            EventOccurrence, pk=event_occurrence_pk)
        if (event_occurrence.host == self.request.user 
                and not event_occurrence.has_passed
                and not event_occurrence.cancelled_ahead
                and not event_occurrence.change_host):
            return event_occurrence
        else:
            raise Http404
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['heading'] = 'Request Day Off?'
        context['action'] = 'request off for'
        context['input_value'] = 'Yes, Request Off'
        return context
        
    def form_valid(self, form):
        form.instance.change_host = True
        messages.info(
            self.request, 'Success! You requested a day off. '
            'Please make sure the details page is up to date '
            'so that your cover can read up on the details.')
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse(
            'event-occurrence-list-host',
            kwargs={'username': self.request.user.username })

class PickUp(LoginRequiredMixin, UpdateView):
    model = EventOccurrence
    context_object_name = 'event_occurrence'
    form_class = ChangeHostForm
    template_name = 'schedule/change_host_form.html'

    def get_object(self, queryset=None):
        event_occurrence_pk = self.kwargs['pk']
        event_occurrence = get_object_or_404(
            EventOccurrence, pk=event_occurrence_pk)
        if (event_occurrence.change_host
                and not event_occurrence.has_passed
                and not event_occurrence.cancelled_ahead):
            return event_occurrence
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['heading'] = 'Pick Up Shift?'
        context['action'] = 'pick up'
        context['input_value'] = 'Yes, Pick Up'
        return context
    
    def form_valid(self, form):
        form.instance.change_host = False
        form.instance.host = self.request.user
        messages.info(
            self.request, 'Thanks for picking up the shift! '
            'Mark your calendar and check the details page '
            'for further information.')
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse(
            'event-occurrence-list-host',
            kwargs={'username': self.request.user.username })
            
def load_days(request):
    state_id = request.GET.get('state')
    if state_id:
        days = Day.objects.filter(event_occurrences__event__venue__state_id=state_id).distinct()
    else:
        days = Day.objects.filter(
            event_occurrences__isnull=False,
            event_occurrences__date__gte=datetime.date.today()).distinct()
    return render(request, 'schedule/day_dropdown_list.html', {'days': days})