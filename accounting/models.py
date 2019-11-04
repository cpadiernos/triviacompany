import datetime
import numpy

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.urls import reverse
from django.utils.translation import ugettext as _

from accounts.models import HostProfile, RegionalManagerProfile
from schedule.models import EventOccurrence

private_event_pay = 150
payday = 4 # Mon = 0, Tues = 1, Wed = 2, etc..

def get_pay_date(date, payday):
    days_left_until_payday = payday - date.weekday()
    if days_left_until_payday <= 0:
        days_left_until_payday += 7
    return date + datetime.timedelta(days_left_until_payday)

def find_pay_stub(user, date):
    pay_date = get_pay_date(date, payday)
    pay_stub, created  = PayStub.objects.get_or_create(
        pay_date=pay_date, user=user)
    while pay_stub.paid:
        pay_date = pay_date + datetime.timedelta(days=7)
        pay_stub, created  = PayStub.objects.get_or_create(
            pay_date=pay_date, user=user)
    return pay_stub

def edited(object, monitored_fields):
    cls = object.__class__
    original = cls.objects.get(pk=object.pk)
    fields = cls._meta.get_fields()
    changed_fields = []
    for field in fields:
        if getattr(original, field.name) != getattr(object, field.name):
            changed_fields.append(field.name)
    monitored_fields = monitored_fields
    if any(field in monitored_fields for field in changed_fields):
        return True

def documentation_path(instance, filename):
    folder = 'reimbursements'
    sub_folder = str(instance.user.username)
    return '{0}/{1}/{2}_{3}'.format(folder, sub_folder, instance.purchase_date, filename)
    
class PayStub(models.Model):
    pay_date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='pay_stubs')
    total_gross_amount = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True)
    total_reimbursement_amount = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    paid = models.BooleanField('paid', default=False)

    class Meta:
        #db_table = "pay_stub"
        ordering = ["pay_date"]
     
    def __str__(self):
        return '{0}: {1} - GROSS: {2}, REIM: {3}'.format(
            self.pay_date, self.user, self.total_gross_amount,
            self.total_reimbursement_amount)

    def get_absolute_url(self):
        return reverse('pay-stub-detail', args=[self.pk])

    def save(self, *args, **kwargs):
        self.calculate_pay()
        if self.paid:
            self.mark_all_paid()
        if self.pk:
            if (not self.total_gross_amount 
                    and not self.total_reimbursement_amount):
                self.delete()
            else:
                super(PayStub, self).save(*args, **kwargs)
        else:
            super(PayStub, self).save(*args, **kwargs)

    def mark_all_paid(self):
        self.salary_payments.all().update(paid=True)
        self.event_occurrence_payments.all().update(paid=True)
        self.reimbursements.all().update(paid=True)

    def calculate_pay(self):
        salary_payments = (SalaryPayment
                              .objects
                              .filter(paid=False, pay_stub=self)
                              .aggregate(sum=Sum('gross_amount')))
        event_occurrence_payments = (EventOccurrencePayment
                                        .objects
                                        .filter(paid=False, pay_stub=self)
                                        .aggregate(sum=Sum('gross_amount')))
        reimbursements = (Reimbursement
                              .objects
                              .filter(paid=False, approved=True, pay_stub=self)
                              .aggregate(sum=Sum('approved_amount')))
        self.total_gross_amount = ((salary_payments['sum'] or 0)
                                  + (event_occurrence_payments['sum'] or 0))
        self.total_reimbursement_amount = reimbursements['sum'] or 0

class SalaryPayment(models.Model):
    week_start = models.DateField(
        null=True, blank=True,
        help_text='First date employee worked, i.e.,\
            employee worked Monday, input Monday\'s date.')
    week_end = models.DateField(
        null=True, blank=True,
        help_text='Date after the last day employee worked,\
            i.e., employee worked Friday, input Saturday\'s date.')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='salary_payments')
    gross_amount = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True)
    pay_stub = models.ForeignKey(
        PayStub, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='salary_payments')
    paid = models.BooleanField('paid', default=False)
    
    class Meta:
        #db_table = "salary_payment"
        ordering = ["week_end"]
    
    def __str__(self):
        return '{0} - {1}: {2} - {3}'.format(
            self.week_start, self.week_end, self.user,
            self.gross_amount)

    def save(self, *args, **kwargs):
        if not self.paid:
            self.calculate_pay()
            pay_stub = find_pay_stub(self.user, self.week_end)
            self.pay_stub = pay_stub
            super(SalaryPayment, self).save(*args, **kwargs)
            pay_stub.save()

    def calculate_pay(self):
        profile = RegionalManagerProfile.objects.get(user=self.user)
        days_worked = numpy.busday_count(self.week_start, self.week_end)
        daily_pay = profile.weekly_pay/5
        pay = days_worked * daily_pay
        self.gross_amount = pay
        
    def clean(self):
        # can set blank = False
        if not self.week_start:
            raise ValidationError(
                {'week_start': ValidationError('', code='required')})
        if not self.week_end:
            raise ValidationError(
                {'week_end': ValidationError('', code='required')})
        if not self.user:
            raise ValidationError(
                {'user': ValidationError('', code='required')})
        #
        if self.user and not self.user.is_regional_manager:
            raise ValidationError(
                {'user': ValidationError(
                    _('Assign a user that is salaried.'), code='invalid')})
        if (self.week_end - self.week_start) > datetime.timedelta(days=7):
            raise ValidationError({
                '__all__': ValidationError(
                    _('Week start and week end must be no more than 7 days apart.'), code='invalid'),
                'week_start': ValidationError(
                    _(''), code='invalid'),
                'week_end': ValidationError(
                    _(''), code='invalid'),
                })
        if self.week_end < self.week_start:
            raise ValidationError({
                '__all__': ValidationError(
                    _('Week start must be before week end'), code='invalid'),
                'week_start': ValidationError(
                    _(''), code='invalid'),
                'week_end': ValidationError(
                    _(''), code='invalid'),
                })

class EventOccurrencePayment(models.Model):

    TYPE = (
        ('R','Regular Event'),
        ('P', 'Private Event'),
    )

    type = models.CharField(
        max_length=1, default="R", choices=TYPE, blank=True)
    submission_date = models.DateField(null=True, blank=True)
    event_occurrence = models.ForeignKey(
        EventOccurrence, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='event_occurrence_payments')
    gross_amount = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    paid = models.BooleanField('paid', default=False)
    pay_stub = models.ForeignKey(
        PayStub, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='event_occurrence_payments')
    
    class Meta:
        #db_table = 'event_occurrence_payment'
        ordering = ['submission_date', 'pay_stub']
    
    def __str__(self):
        return '{0} {1} {2} {3}'.format(
            self.type, self.submission_date,
            self.event_occurrence, self.gross_amount)

    def save(self, *args, **kwargs):
        if not self.paid:
            if self.type == 'R' and self.event_occurrence.is_complete:
                self.calculate_pay()
            if self.event_occurrence.event.is_private == True:
                    self.type = 'P'
                    self.gross_amount = private_event_pay
            if self.pk:
                fields = ['gross_amount']
                if edited(self, fields):
                    self.submission_date = datetime.date.today()
            else:
                self.submission_date = datetime.date.today()
            pay_stub = find_pay_stub(self.event_occurrence.host, self.submission_date)
            self.pay_stub = pay_stub
            super(EventOccurrencePayment, self).save(*args, **kwargs)
            pay_stub.save()

    def clean(self):
        # can set blank = False
        if not self.event_occurrence:
            raise ValidationError({
                'event_occurrence': ValidationError(_(''),
                code='required')})

    def calculate_pay(self):
        host, created = HostProfile.objects.get_or_create(
            user=self.event_occurrence.host)
        number_of_teams = self.event_occurrence.number_of_teams or 0
        if number_of_teams >= host.base_teams:
            self.gross_amount = round((host.base_rate
                                + (number_of_teams - host.base_teams)
                                * host.incremental_rate), 2)
        elif number_of_teams < host.base_teams:
            self.gross_amount = host.base_rate

    def display_event_date(self):
        return self.event_occurrence.date
    display_event_date.short_description = 'Occurrence Date'
    
    def display_event(self):
        return self.event_occurrence.event
    display_event.short_description = 'Event'
    
    def display_host(self):
        return self.event_occurrence.host
    display_host.short_description = 'Host'
    
    def display_number_of_teams(self):
        return self.event_occurrence.number_of_teams
    display_number_of_teams.short_description = 'Number of Teams'

class Reimbursement(models.Model):
    submission_date = models.DateField(null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    
    CATEGORY = (
        ('F/D','Food or Drink'),
        ('GS', 'Game Supplies'),
        ('E', 'Equipment'),
        ('T', 'Transportation'),
    )

    category = models.CharField(max_length=20, choices=CATEGORY, blank=True)
    description = models.TextField(blank=True)
    amount = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text='Only enter amount. Do not add "$". Example, 2.25.')
    documentation = models.FileField(upload_to=documentation_path, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='reimbursements')
    pay_stub = models.ForeignKey(
        PayStub, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='reimbursements')
    approved = models.BooleanField('approved', default=False)
    approved_amount = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    paid = models.BooleanField('paid', default=False)

    class Meta:
        #db_table = "reimbursement"
        ordering = ["-submission_date", "pay_stub"]
     
    def __str__(self):
        return '{0}: {1} - {2}'.format(
            self.purchase_date, self.category, self.amount)
     
    def save(self, *args, **kwargs):
        if self.pk:
            fields = ['purchase_date', 'category', 'description',
                     'amount', 'documentation', 'user']
            if edited(self, fields):
                self.approved = False
                self.submission_date = datetime.date.today()
        else:
            self.submission_date = datetime.date.today()

        if not self.paid:
            if self.approved:
                pay_stub = find_pay_stub(self.user, self.submission_date)
                self.pay_stub = pay_stub
                super(Reimbursement, self).save(*args, **kwargs)
                pay_stub.save()
            elif not self.approved:
                self.approved_amount = None
                if self.pay_stub:
                    pay_stub = self.pay_stub
                    self.pay_stub = None
                    super(Reimbursement, self).save(*args, **kwargs)
                    pay_stub.save()
                else:
                    super(Reimbursement, self).save(*args, **kwargs)

    def clean(self):
        if self.approved and not self.approved_amount:
            raise ValidationError({
                'approved_amount': ValidationError(
                    _(''), code='required')})