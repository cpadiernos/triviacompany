import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from .forms import ReimbursementForm
from .models import PayStub, Reimbursement, EventOccurrencePayment

class PayStubDetailView(LoginRequiredMixin, DetailView):
    model = PayStub
    context_object_name = 'pay_stub'
    template_name = 'accounting/pay_stub_detail.html'

    def get_queryset(self):
        pay_stub = PayStub.objects.filter(user=self.request.user)
        return pay_stub

class BelongsToUserInUrlMixin(ListView):
    def get_queryset(self):
        if self.kwargs['username'] == self.request.user.username:
            obj_user = self.model.objects.filter(user=self.request.user)
            return obj_user
        else:
            raise Http404

class PayStubListViewUser(LoginRequiredMixin, BelongsToUserInUrlMixin):
    model = PayStub
    context_object_name = 'pay_stub_list'
    template_name = 'accounting/pay_stub_list.html'

class PayStubListViewCurrentUser(PayStubListViewUser):
    
    def get_queryset(self):
        pay_stub_user = super().get_queryset()
        pay_stub_current_user = pay_stub_user.filter(pay_date__gte=datetime.datetime.now())
        return pay_stub_current_user

class PayStubListViewPastUser(PayStubListViewUser):
    
    def get_queryset(self):
        pay_stub_user = super().get_queryset()
        pay_stub_past_user = pay_stub_user.filter(pay_date__lte=datetime.datetime.now()).order_by('-pay_date')
        return pay_stub_past_user

class ReimbursementCreateView(LoginRequiredMixin, CreateView):
    form_class = ReimbursementForm
    template_name = 'accounting/reimbursement_create.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('reimbursement-list-user', args=[self.request.user])

class ReimbursementListViewUser(LoginRequiredMixin, BelongsToUserInUrlMixin):
    model = Reimbursement
    template_name='accounting/reimbursement_list.html'

class ReimbursementUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ReimbursementForm
    template_name = 'accounting/reimbursement_create.html'

    def get_object(self, queryset=None):
        reimbursement_pk = self.kwargs['pk']
        reimbursement = get_object_or_404(
            Reimbursement, pk=reimbursement_pk)
        if reimbursement.user == self.request.user:
            return reimbursement
        else:
            raise Http404
            
    def get_success_url(self):
        return reverse(
            'reimbursement-list-user',
            kwargs={'username': self.request.user.username })