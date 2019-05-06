from django.contrib import admin
from .models import Region, State, City, Zip, Venue, ManagementPeriod

admin.site.register(Region)

class StateAdmin(admin.ModelAdmin):
    model = State
    list_display = ('name', 'region')
    list_filter = ('region', 'name')

admin.site.register(State, StateAdmin)

class CityAdmin(admin.ModelAdmin):
    model = City
    list_display = ('name', 'state')
    list_filter = ('state__region', 'state', 'name')

admin.site.register(City, CityAdmin)

class ZipAdmin(admin.ModelAdmin):
    model = Zip
    list_display = ('code', 'city')
    list_filter = ('city__name', 'city__state')
    search_fields = ['code']
    
admin.site.register(Zip, ZipAdmin)

class ManagementPeriodInline(admin.TabularInline):
    model = ManagementPeriod
    extra = 0

class VenueAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'address', 'additional_address', 'city', 'state', 'zip',
        'email', 'phone_number', 'display_manager')
    list_filter = ('state__region', 'state')
    inlines = [ManagementPeriodInline]

admin.site.register(Venue, VenueAdmin)