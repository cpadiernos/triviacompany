from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Policy, Section

class PolicyListView(generic.ListView):
    model = Policy
    context_object_name = 'policy_list'
    template_name = 'policies/policy_list.html'
    
class PolicyCreate(CreateView):
    model = Policy
    fields = ('name', 'detail')
    template_name = 'policies/policy_form.html'
    success_url = reverse_lazy('policy-list')
    
class PolicyUpdate(UpdateView):
    model = Policy
    fields = ('name', 'detail')
    template_name = 'policies/policy_form.html'
    success_url = reverse_lazy('policy-list')

class PolicyDelete(DeleteView):
    model = Policy
    context_object_name = 'policy'
    template_name = 'policies/policy_confirm_delete.html'
    success_url = reverse_lazy('policy-list')

class SectionCreate(CreateView):
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

class SectionUpdate(UpdateView):
    model = Section
    fields = ('name', 'detail')
    template_name = 'policies/section_form.html'
    pk_url_kwarg = 'section_pk'
    success_url = reverse_lazy('policy-list')
    
    def get_queryset(self):
        return Section.objects.filter(policy__pk=self.kwargs['policy_pk']) 
    
class SectionDelete(DeleteView):
    model = Section
    context_object_name = 'section'
    template_name = 'policies/section_confirm_delete.html'
    pk_url_kwarg = 'section_pk'
    success_url = reverse_lazy('policy-list')
    
    def get_queryset(self):
        return Section.objects.filter(policy__pk=self.kwargs['policy_pk'])
    
class SectionMove(UpdateView):
    model = Section
    fields = ['policy']
    template_name = 'policies/section_form.html'
    pk_url_kwarg = 'section_pk'
    success_url = reverse_lazy('policy-list')

    def get_queryset(self):
        return Section.objects.filter(policy__pk=self.kwargs['policy_pk']) 