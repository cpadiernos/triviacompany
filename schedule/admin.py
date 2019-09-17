from django.contrib import admin, messages
from .models import Day, Time, Event, EventImage, EventOccurrence

admin.site.register(Day)
admin.site.register(Time)

def generate_event_occurrences_from_event(modeladmin, request, queryset):
    total = 0
    for object in queryset:
        if not object.start_date:
            messages.error(request, 'Did not generate occurrences for {0} because it needs a start date.'.format(object))
        generated = object.generate_event_occurrences()
        total += generated
    if total == 0:
        messages.warning(request, 'No event occurrences were generated.')
    else:
        messages.success(
            request,
            'Successfully generated {0} event occurrences.'.format(total))
generate_event_occurrences_from_event.short_description = "Generate event occurrences (up to 8 weeks)"

class EventOccurrenceInline(admin.TabularInline):
    model = EventOccurrence
    extra = 0
    classes = ['collapse']

class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 0

class EventAdmin(admin.ModelAdmin):
    list_display = (
        'venue', 'host', 'day', 'time', 'start_date', 'end_date', 'status',
        'request_future_restart', 'base_teams', 'base_rate',
        'incremental_teams', 'incremental_rate')
    fieldsets = (
        (None, {
            'fields': (
                'venue', 'host', 'day', 'time', 'start_date', 'end_date',
                'status', 'request_future_restart')
        }),
        ('Prizes', {
            'fields': (
                'first_place_prize', 'second_place_prize',
                'third_place_prize', 'additional_prize_info')
        }),
        ('Rate', {
            'fields': (
                'base_teams', 'base_rate',
                'incremental_teams', 'incremental_rate')
        }),
    )
    inlines = (EventOccurrenceInline, EventImageInline)
    actions = [generate_event_occurrences_from_event]

admin.site.register(Event, EventAdmin)

class EventImageAdmin(admin.ModelAdmin):
    model = EventImage

admin.site.register(EventImage, EventImageAdmin)

class EventOccurrenceAdmin(admin.ModelAdmin):
    list_display = (
        'event', 'day', 'time', 'date', 'host', 'change_host',
        'status', 'cancellation_reason', 'cancelled_ahead', 'time_started',
        'display_game_length', 'number_of_teams', 'scoresheet', 'notes')
    list_filter = (
        ('event__venue', admin.RelatedOnlyFieldListFilter),
        ('host' , admin.RelatedOnlyFieldListFilter),
        ('day', admin.RelatedOnlyFieldListFilter),
        'status', 'change_host')

admin.site.register(EventOccurrence, EventOccurrenceAdmin)