from django.shortcuts import render
from django.views import generic

from .models import HostProfile

class HostProfileListView(generic.ListView):
    model = HostProfile
    context_object_name = 'host_profile_list'
    template_name = 'accounts/host_profile_list.html'