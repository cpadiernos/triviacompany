from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import HostProfile, VenueManagerProfile, RegionalManagerProfile
from .forms import CustomUserCreationForm, CustomUserChangeForm

class HostProfileAdmin(admin.ModelAdmin):
    model = HostProfile
    list_display = (
        'user', 'bio', 'has_event',
        'base_teams', 'base_rate', 'incremental_teams', 'incremental_rate')

admin.site.register(HostProfile, HostProfileAdmin)

class HostProfileInline(admin.StackedInline):
    model = HostProfile
    can_delete = False
    verbose_name_plural = 'Host Profile'

class RegionalManagerProfileAdmin(admin.ModelAdmin):
    model = RegionalManagerProfile
    list_display = ('user', 'region', 'weekly_pay')

admin.site.register(RegionalManagerProfile, RegionalManagerProfileAdmin)

class RegionalManagerProfileInline(admin.StackedInline):
    model = RegionalManagerProfile
    can_delete = False
    verbose_name_plural = 'Regional Manager Profile'

class VenueManagerProfileAdmin(admin.ModelAdmin):
    model = VenueManagerProfile
    list_display = (
        'user', 'best_reached_by', 'display_preferred_communication')

admin.site.register(VenueManagerProfile, VenueManagerProfileAdmin)

class VenueManagerProfileInline(admin.StackedInline):
    model = VenueManagerProfile
    can_delete = False
    verbose_name_plural = 'Venue Manager Profile'

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    inlines = (
        HostProfileInline,
        RegionalManagerProfileInline,
        VenueManagerProfileInline
        )

    list_filter = ('is_host', 'is_regional_manager', 'is_venue_manager')
    list_display = (
        'username', 'email', 'is_active', 'is_staff',
        'is_regional_manager', 'is_host', 'is_venue_manager',
        'mobile_number', 'mailing_city', 'mailing_state',
        'last_login')

    add_fieldsets = (
        (None, {
            'fields': ('username', 'first_name', 'last_name',
                       'email', 'password1', 'password2', 'groups',
                       'is_active', 'is_staff',
                       'is_regional_manager', 'is_host', 'is_venue_manager',
                       'secondary_email',
                       'mobile_number', 'work_number',
                       'mailing_address', 'mailing_additional_address',
                       'mailing_state', 'mailing_city', 'mailing_zip',
                       'profile_image')
        }),
    )

    fieldsets = (
        (None, {
            'fields': ('username', 'first_name', 'last_name',
                       'email', 'password', 'groups',
                       'is_active', 'is_staff',
                       'is_regional_manager', 'is_host', 'is_venue_manager',
                       'secondary_email',
                       'mobile_number', 'work_number',
                       'mailing_address', 'mailing_additional_address',
                       'mailing_state', 'mailing_city', 'mailing_zip',
                       'profile_image')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)