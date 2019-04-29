from django.contrib import admin
from .models import Policy, Section

class PolicyAdmin(admin.ModelAdmin):
    model = Policy
    list_display = ('name', 'detail')
    
admin.site.register(Policy, PolicyAdmin)

class SectionAdmin(admin.ModelAdmin):
    model = Section
    list_display = ('policy', 'name', 'detail')
    list_filter = ['policy']
    list_display_links = ['name']
    
admin.site.register(Section, SectionAdmin)
