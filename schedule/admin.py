from django.contrib import admin
from .models import Day, Time, Event, EventImage, EventOccurrence

admin.site.register(Day)
admin.site.register(Time)

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

admin.site.register(Event, EventAdmin)

class EventImageAdmin(admin.ModelAdmin):
    model = EventImage

admin.site.register(EventImage, EventImageAdmin)

class EventOccurrenceAdmin(admin.ModelAdmin):
    list_display = (
        'event', 'day', 'time', 'date', 'host', 'change_host',
        'status', 'cancellation_reason', 'cancelled_ahead', 'time_started',
        'display_game_length', 'number_of_teams', 'scoresheet', 'notes')

admin.site.register(EventOccurrence, EventOccurrenceAdmin)