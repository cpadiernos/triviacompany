from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Policy, Section

class UserIsRegionalManagerMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_regional_manager
    
def employee_check(user):
    return user.is_host or user.is_regional_manager

class PolicyListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = Policy
    context_object_name = 'policy_list'
    template_name = 'policies/policy_list.html'

    def test_func(self):
        return employee_check(self.request.user)

class PolicyCreate(LoginRequiredMixin, UserIsRegionalManagerMixin, CreateView):
    model = Policy
    fields = ('name', 'detail')
    template_name = 'policies/policy_form.html'
    success_url = reverse_lazy('policy-list')

class PolicyUpdate(LoginRequiredMixin, UserIsRegionalManagerMixin, UpdateView):
    model = Policy
    fields = ('name', 'detail')
    template_name = 'policies/policy_form.html'
    success_url = reverse_lazy('policy-list')

class PolicyDelete(LoginRequiredMixin, UserIsRegionalManagerMixin, DeleteView):
    model = Policy
    context_object_name = 'policy'
    template_name = 'policies/confirm_delete.html'
    success_url = reverse_lazy('policy-list')

class SectionCreate(LoginRequiredMixin, UserIsRegionalManagerMixin, CreateView):
    model = Section
    template_name = 'policies/section_form.html'
    fields = ('name', 'detail')
    success_url = reverse_lazy('policy-list')

    def get(self, request, *args, **kwargs):
        get_object_or_404(Policy, pk=self.kwargs['pk'])
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.policy = get_object_or_404(Policy, pk=self.kwargs['pk'])
        return super().form_valid(form)

class SectionUpdate(LoginRequiredMixin, UserIsRegionalManagerMixin, UpdateView):
    model = Section
    fields = ('name', 'detail')
    template_name = 'policies/section_form.html'
    pk_url_kwarg = 'section_pk'
    success_url = reverse_lazy('policy-list')
    
    def get_queryset(self):
        return Section.objects.filter(policy__pk=self.kwargs['policy_pk']) 
    
class SectionDelete(LoginRequiredMixin, UserIsRegionalManagerMixin, DeleteView):
    model = Section
    context_object_name = 'section'
    template_name = 'policies/confirm_delete.html'
    pk_url_kwarg = 'section_pk'
    success_url = reverse_lazy('policy-list')
    
    def get_queryset(self):
        return Section.objects.filter(policy__pk=self.kwargs['policy_pk'])
    
class SectionMove(LoginRequiredMixin, UserIsRegionalManagerMixin, UpdateView):
    model = Section
    fields = ['policy']
    template_name = 'policies/section_form.html'
    pk_url_kwarg = 'section_pk'
    success_url = reverse_lazy('policy-list')

    def get_queryset(self):
        return Section.objects.filter(policy__pk=self.kwargs['policy_pk']) 