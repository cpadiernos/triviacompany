from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import UpdateView

from .models import HostProfile, CustomUser
from .forms import CustomUserUpdateForm

class HostProfileListView(generic.ListView):
    model = HostProfile
    context_object_name = 'host_profile_list'
    template_name = 'accounts/host_profile_list.html'

class CustomUserUpdate(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = 'accounts/custom_user_form.html'

    def get_object(self, queryset=None):
        username = self.kwargs['username']
        user = get_object_or_404(CustomUser, username=username)
        if username == self.request.user.username:
            return user
        else:
            raise Http404

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        messages.info(self.request, 'Your account has been updated!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'account-update',
            kwargs={'username': self.request.user.username })