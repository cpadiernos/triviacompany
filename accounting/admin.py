from django.contrib import admin
from .models import PayStub, SalaryPayment, EventOccurrencePayment, Reimbursement

class ReadOnlyIfPaidMixin(admin.ModelAdmin):
     def get_readonly_fields(self, request, obj=None):
        if obj and obj.paid:
          return self.readonly_fields + tuple([field.name for field in obj._meta.fields])
        return self.readonly_fields
        
class PayStubAdmin(ReadOnlyIfPaidMixin):
    model = PayStub
    list_display = ('pay_date', 'user', 'total_gross_amount', 'total_reimbursement_amount', 'paid')
    list_filter = (('user', admin.RelatedOnlyFieldListFilter), 'paid')

admin.site.register(PayStub, PayStubAdmin)

class SalaryPaymentAdmin(ReadOnlyIfPaidMixin):
    model = SalaryPayment
    list_display = ('week_start', 'week_end', 'user', 'gross_amount', 'pay_stub', 'paid')
    list_filter = [('user', admin.RelatedOnlyFieldListFilter)]

admin.site.register(SalaryPayment, SalaryPaymentAdmin)

class EventOccurrencePaymentAdmin(ReadOnlyIfPaidMixin):
    model = EventOccurrencePayment
    list_display = ('type', 'submission_date', 'display_event_date', 'display_event', 'display_host', 'display_number_of_teams', 'gross_amount', 'pay_stub', 'paid')
    list_filter=('type', ('event_occurrence__host', admin.RelatedOnlyFieldListFilter), ('event_occurrence__event__venue', admin.RelatedOnlyFieldListFilter), 'paid')

admin.site.register(EventOccurrencePayment, EventOccurrencePaymentAdmin)

class ReimbursementAdmin(ReadOnlyIfPaidMixin):
    model = Reimbursement
    list_display = ('submission_date', 'purchase_date', 'category', 'description', 'amount', 'documentation', 'user', 'pay_stub', 'approved', 'approved_amount', 'paid')
    list_filter = (('user', admin.RelatedOnlyFieldListFilter), 'approved')

admin.site.register(Reimbursement, ReimbursementAdmin)
