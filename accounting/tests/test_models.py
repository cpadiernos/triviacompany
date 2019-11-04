import datetime
import shutil

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from accounting.models import PayStub, SalaryPayment, EventOccurrencePayment, Reimbursement
from accounting.models import get_pay_date, find_pay_stub, edited, documentation_path
from accounts.models import CustomUser, RegionalManagerProfile, HostProfile
from schedule.models import Day, Event, EventOccurrence

class ModelUtilsTests(TestCase):
    def test_get_pay_date(self):
        payday = 4 # Friday
        date = datetime.date(2019, 8, 5)
        result = get_pay_date(date, payday)
        self.assertEqual(result, datetime.date(2019, 8, 9))

    def test_find_pay_stub_closest_unpaid_found(self):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        date = datetime.date(2019, 8, 5)
        result = find_pay_stub(user, date)
        pay_stub = PayStub.objects.first()
        self.assertIsInstance(result, PayStub)
        self.assertEqual(result.pay_date, datetime.date(2019, 8, 9))

    def test_find_pay_stub_next_closest_unpaid_found(self):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        pay_stub = PayStub.objects.create(
            user=user, pay_date=datetime.date(2019, 8, 9),
            paid=True)
        date = datetime.date(2019, 8, 5)
        result = find_pay_stub(user, date)
        self.assertIsInstance(result, PayStub)
        self.assertEqual(PayStub.objects.all().count(), 2)
        self.assertEqual(result.pay_date, datetime.date(2019, 8, 16))

    def test_edited_true(self):
        reimbursement = Reimbursement.objects.create()
        monitored_field = ['purchase_date']
        reimbursement = Reimbursement.objects.get(pk=1)
        reimbursement.purchase_date = datetime.date.today()
        self.assertTrue(edited(reimbursement, monitored_field))
        
    def test_edited_false(self):
        reimbursement = Reimbursement.objects.create()
        monitored_field = ['purchase_date']
        reimbursement = Reimbursement.objects.get(pk=1)
        reimbursement.amount = '2.00'
        self.assertFalse(edited(reimbursement, monitored_field))

    def test_documentation_path(self):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        reimbursement = Reimbursement.objects.create(
            user=user,
            purchase_date=datetime.date(2019, 8, 5))
        result = documentation_path(reimbursement , 'test_file.txt')
        self.assertEqual(result, 'reimbursements/carol/2019-08-05_test_file.txt')
        
class PayStubModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        pay_stub = PayStub.objects.create(user=user)

    def test_pay_date_label(self):
        pay_stub = PayStub.objects.get(pk=1)
        field_label = pay_stub._meta.get_field('pay_date').verbose_name
        self.assertEqual(field_label, 'pay date')

    def test_pay_date_null(self):
        pay_stub = PayStub.objects.get(pk=1)
        null = pay_stub._meta.get_field('pay_date').null
        self.assertEqual(null, True)

    def test_pay_date_blank(self):
        pay_stub = PayStub.objects.get(pk=1)
        blank = pay_stub._meta.get_field('pay_date').blank
        self.assertEqual(blank, True)

    def test_user_label(self):
        pay_stub = PayStub.objects.get(pk=1)
        field_label = pay_stub._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_user_null_on_delete(self):
        user = CustomUser.objects.get(pk=1)
        user.delete()
        user_count = CustomUser.objects.all().count()
        pay_stub_count = PayStub.objects.all().count()
        pay_stub = PayStub.objects.get(pk=1)
        self.assertEqual(user_count, 0)
        self.assertEqual(pay_stub_count, 1)
        self.assertEqual(pay_stub.user, None)

    def test_user_null(self):
        pay_stub = PayStub.objects.get(pk=1)
        null = pay_stub._meta.get_field('user').null
        self.assertEqual(null, True)

    def test_user_blank(self):
        pay_stub = PayStub.objects.get(pk=1)
        blank = pay_stub._meta.get_field('user').blank
        self.assertEqual(blank, True)

    def test_user_related_name_is_pay_stubs(self):
        pay_stub = PayStub.objects.get(pk=1)
        related_name = pay_stub.user._meta.get_field('pay_stubs').related_name
        self.assertEqual(related_name, 'pay_stubs')

    def test_total_gross_amount_label(self):
        pay_stub = PayStub.objects.get(pk=1)
        field_label = pay_stub._meta.get_field('total_gross_amount').verbose_name
        self.assertEqual(field_label, 'total gross amount')

    def test_total_gross_amount_max_digits(self):
        pay_stub = PayStub.objects.get(pk=1)
        max_digits = pay_stub._meta.get_field('total_gross_amount').max_digits
        self.assertEqual(max_digits, 6)

    def test_total_gross_amount_decimal_places(self):
        pay_stub = PayStub.objects.get(pk=1)
        decimal_places = pay_stub._meta.get_field('total_gross_amount').decimal_places
        self.assertEqual(decimal_places, 2)

    def test_total_gross_amount_null(self):
        pay_stub = PayStub.objects.get(pk=1)
        null = pay_stub._meta.get_field('total_gross_amount').null
        self.assertEqual(null, True)

    def test_total_gross_amount_blank(self):
        pay_stub = PayStub.objects.get(pk=1)
        blank = pay_stub._meta.get_field('total_gross_amount').blank
        self.assertEqual(blank, True)

    def test_total_reimbursement_amount_label(self):
        pay_stub = PayStub.objects.get(pk=1)
        field_label = pay_stub._meta.get_field('total_reimbursement_amount').verbose_name
        self.assertEqual(field_label, 'total reimbursement amount')

    def test_total_reimbursement_amount_max_digits(self):
        pay_stub = PayStub.objects.get(pk=1)
        max_digits = pay_stub._meta.get_field('total_reimbursement_amount').max_digits
        self.assertEqual(max_digits, 5)

    def test_total_reimbursement_amount_decimal_places(self):
        pay_stub = PayStub.objects.get(pk=1)
        decimal_places = pay_stub._meta.get_field('total_reimbursement_amount').decimal_places
        self.assertEqual(decimal_places, 2)

    def test_total_reimbursement_amount_null(self):
        pay_stub = PayStub.objects.get(pk=1)
        null = pay_stub._meta.get_field('total_reimbursement_amount').null
        self.assertEqual(null, True)

    def test_total_reimbursement_amount_blank(self):
        pay_stub = PayStub.objects.get(pk=1)
        blank = pay_stub._meta.get_field('total_reimbursement_amount').blank
        self.assertEqual(blank, True)

    def test_paid_label(self):
        pay_stub = PayStub.objects.get(pk=1)
        field_label = pay_stub._meta.get_field('paid').verbose_name
        self.assertEqual(field_label, 'paid')

    def test_paid_default(self):
        pay_stub = PayStub.objects.get(pk=1)
        default = pay_stub._meta.get_field('paid').default
        self.assertEqual(default, False)

    def test_str(self):
        pay_stub = PayStub.objects.get(pk=1)
        self.assertEqual(
            str(pay_stub),
            '{0}: {1} - GROSS: {2}, REIM: {3}'.format(
                pay_stub.pay_date,
                pay_stub.user,
                pay_stub.total_gross_amount,
                pay_stub.total_reimbursement_amount))

    def test_get_absolute_url(self):
        pay_stub = PayStub.objects.get(pk=1)
        self.assertEqual(
            pay_stub.get_absolute_url(),
            reverse('pay-stub-detail', args=[pay_stub.pk]))

    def test_save_on_creation_has_no_value(self):
        pay_stub = PayStub.objects.get(pk=1)
        self.assertEqual(pay_stub.total_gross_amount, 0)
        self.assertEqual(pay_stub.total_reimbursement_amount, 0)
        
    def test_save_no_gross_pay_and_no_reimbursement_pay_self_deletes(self):
        pay_stub = PayStub.objects.get(pk=1)
        pay_stub.save()
        pay_stub_count = PayStub.objects.all().count()
        self.assertEqual(pay_stub_count, 0)

    def test_calculate_pay_with_salary_and_event_occurrence_payment(self):
        user = CustomUser.objects.get(pk=1)
        regional_manager_profile = RegionalManagerProfile.objects.create(
            user=user, weekly_pay=950.00)
        salary_payment = SalaryPayment.objects.create(
            week_start=datetime.date.today() - datetime.timedelta(days=7),
            week_end=datetime.date.today(),
            user=user)
        host_profile = HostProfile.objects.create(
            user=user,
            base_teams=5, base_rate=50,
            incremental_teams=1, incremental_rate=5)
        day = Day.objects.create(day=datetime.date.today().weekday())
        event = Event.objects.create(
            day=day,
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=28),
            host=user)
        event_occurrence = EventOccurrence.objects.create(
            event=event,
            host=user, date=datetime.date.today(),
            status='Game',
            time_started=datetime.time(20,15),
            time_ended = datetime.time(22,15),
            number_of_teams=6)
        event_occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        total_gross_amount = event_occurrence_payment.gross_amount \
                             + salary_payment.gross_amount
        self.assertEqual(salary_payment.pay_stub,
            event_occurrence_payment.pay_stub)
        self.assertEqual(event_occurrence_payment.pay_stub.total_gross_amount,
            total_gross_amount)

    def test_calculate_pay_with_unapproved_reimbursement(self):
        user = CustomUser.objects.get(pk=1)
        reimbursement = Reimbursement.objects.create(
            user=user,
            amount=2.50)
        self.assertEqual(reimbursement.pay_stub, None)

    def test_calculate_pay_with_approved_reimbursement(self):
        user = CustomUser.objects.get(pk=1)
        reimbursement = Reimbursement.objects.create(
            user=user,
            amount=2.50,
            approved=True,
            approved_amount=2.50)
        self.assertEqual(
            reimbursement.pay_stub.total_reimbursement_amount, 2.50)

    def test_mark_all_paid(self):
        user = CustomUser.objects.get(pk=1)
        regional_manager_profile = RegionalManagerProfile.objects.create(
            user=user, weekly_pay=950.00)
        salary_payment = SalaryPayment.objects.create(
            week_start=datetime.date.today() - datetime.timedelta(days=7),
            week_end=datetime.date.today(),
            user=user)
        host_profile = HostProfile.objects.create(
            user=user,
            base_teams=5, base_rate=50,
            incremental_teams=1, incremental_rate=5)
        day = Day.objects.create(day=datetime.date.today().weekday())
        event = Event.objects.create(
            day=day,
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=28),
            host=user)
        event_occurrence = EventOccurrence.objects.create(
            event=event,
            host=user, date=datetime.date.today(),
            status='Game',
            time_started=datetime.time(20,15),
            time_ended = datetime.time(22,15),
            number_of_teams=6)
        event_occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        total_gross_amount = event_occurrence_payment.gross_amount \
                             + salary_payment.gross_amount
        reimbursement = Reimbursement.objects.create(
            user=user,
            amount=2.50,
            approved=True,
            approved_amount=2.50)
        pay_stub = reimbursement.pay_stub
        pay_stub.paid = True
        pay_stub.save()
        salary_payment.refresh_from_db()
        event_occurrence_payment.refresh_from_db()
        reimbursement.refresh_from_db()
        self.assertEqual(
            reimbursement.pay_stub \
            == salary_payment.pay_stub \
            == event_occurrence_payment.pay_stub,
            True)
        self.assertTrue(reimbursement.paid)
        self.assertTrue(salary_payment.paid)
        self.assertTrue(event_occurrence_payment.paid)

class SalaryPaymentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti',
            is_regional_manager=True)
        regional_manager_profile = RegionalManagerProfile.objects.create(
            user=user, weekly_pay=950.00)
        salary_payment = SalaryPayment.objects.create(
            week_start=datetime.date.today() - datetime.timedelta(days=7),
            week_end=datetime.date.today(),
            user=user)

    def test_week_start_label(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        field_label = salary_payment._meta.get_field('week_start').verbose_name
        self.assertEqual(field_label, 'week start')

    def test_week_start_null(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        null = salary_payment._meta.get_field('week_start').null
        self.assertTrue(null)

    def test_week_start_blank(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        blank= salary_payment._meta.get_field('week_start').blank
        self.assertTrue(blank)

    def test_week_end_label(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        field_label = salary_payment._meta.get_field('week_end').verbose_name
        self.assertEqual(field_label, 'week end')

    def test_week_end_null(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        null = salary_payment._meta.get_field('week_end').null
        self.assertTrue(null)

    def test_week_end_blank(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        blank= salary_payment._meta.get_field('week_end').blank
        self.assertTrue(blank)

    def test_user_label(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        field_label = salary_payment._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_user_null_on_delete(self):
        user = CustomUser.objects.get(pk=1)
        user.delete()
        user_count = CustomUser.objects.all().count()
        salary_payment_count = SalaryPayment.objects.all().count()
        salary_payment = SalaryPayment.objects.get(pk=1)
        self.assertEqual(user_count, 0)
        self.assertEqual(salary_payment_count, 1)
        self.assertEqual(salary_payment.user, None)

    def test_user_null(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        null = salary_payment._meta.get_field('user').null
        self.assertEqual(null, True)

    def test_user_blank(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        blank = salary_payment._meta.get_field('user').blank
        self.assertEqual(blank, True)

    def test_user_related_name_is_salary_payments(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        related_name = salary_payment.user._meta.get_field('salary_payments').related_name
        self.assertEqual(related_name, 'salary_payments')

    def test_gross_amount_label(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        field_label = salary_payment._meta.get_field('gross_amount').verbose_name
        self.assertEqual(field_label, 'gross amount')

    def test_gross_amount_max_digits(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        max_digits = salary_payment._meta.get_field('gross_amount').max_digits
        self.assertEqual(max_digits, 6)

    def test_gross_amount_decimal_places(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        decimal_places = salary_payment._meta.get_field('gross_amount').decimal_places
        self.assertEqual(decimal_places, 2)

    def test_gross_amount_null(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        null = salary_payment._meta.get_field('gross_amount').null
        self.assertEqual(null, True)

    def test_gross_amount_blank(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        blank = salary_payment._meta.get_field('gross_amount').blank
        self.assertEqual(blank, True)

    def test_pay_stub_label(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        field_label = salary_payment._meta.get_field('pay_stub').verbose_name
        self.assertEqual(field_label, 'pay stub')

    def test_pay_stub_class(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        model = salary_payment._meta.get_field('pay_stub').related_model
        self.assertEqual(model, PayStub)

    def test_pay_stub_null_on_delete(self):
        pay_stub = PayStub.objects.get(pk=1)
        pay_stub.delete()
        pay_stub_count = PayStub.objects.all().count()
        salary_payment_count = SalaryPayment.objects.all().count()
        salary_payment = SalaryPayment.objects.get(pk=1)
        self.assertEqual(pay_stub_count, 0)
        self.assertEqual(salary_payment_count, 1)
        self.assertEqual(salary_payment.pay_stub, None)

    def test_pay_stub_null(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        null = salary_payment._meta.get_field('pay_stub').null
        self.assertEqual(null, True)

    def test_pay_stub_blank(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        blank = salary_payment._meta.get_field('pay_stub').blank
        self.assertEqual(blank, True)

    def test_pay_stub_related_name_is_salary_payments(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        related_name = salary_payment.pay_stub._meta.get_field('salary_payments').related_name
        self.assertEqual(related_name, 'salary_payments')

    def test_paid_label(self):
        pay_stub = PayStub.objects.get(pk=1)
        field_label = pay_stub._meta.get_field('paid').verbose_name
        self.assertEqual(field_label, 'paid')

    def test_paid_default(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        default = salary_payment._meta.get_field('paid').default
        self.assertEqual(default, False)

    def test_str_(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        self.assertEqual(
            str(salary_payment),
            '{0} - {1}: {2} - {3}'.format(
            salary_payment.week_start,
            salary_payment.week_end,
            salary_payment.user,
            salary_payment.gross_amount))

    def test_calculate_pay_week(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        user = salary_payment.user
        user_pay = user.regional_manager_profile.weekly_pay
        self.assertEqual(salary_payment.gross_amount, user_pay)

    def test_calculate_pay_two_days_fri_and_mon(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        date = datetime.date.today()
        while date.weekday() != 4: # Friday
            date += datetime.timedelta(days=1)
        salary_payment.week_start = date
        salary_payment.week_end = date + datetime.timedelta(days=4)
        user = salary_payment.user
        salary_payment.save()
        weekly_pay = user.regional_manager_profile.weekly_pay
        daily_pay = weekly_pay/5
        pay = daily_pay * 2
        self.assertEqual(salary_payment.gross_amount, pay)

    def test_save_not_paid(self):
        salary_payment = SalaryPayment.objects.get(pk=1)
        original = salary_payment.gross_amount
        salary_payment.paid = False
        date = datetime.date.today()
        while date.weekday() != 4: # Friday
            date += datetime.timedelta(days=1)
        salary_payment.week_start = date
        salary_payment.week_end = date + datetime.timedelta(days=5)
        salary_payment.save()
        self.assertNotEqual(salary_payment.gross_amount, original)

    def test_save_paid_change_amount(self):
        salary_payment_query = SalaryPayment.objects.filter(pk=1)
        salary_payment_query.update(paid = True)
        salary_payment = SalaryPayment.objects.get(pk=1)
        original = salary_payment.gross_amount
        salary_payment.gross_amount = 500
        salary_payment.save()
        salary_payment.refresh_from_db()
        self.assertEqual(salary_payment.gross_amount, original)

    def test_save_change_date(self):
        salary_payment_query = SalaryPayment.objects.filter(pk=1)
        salary_payment_query.update(paid = True)
        salary_payment = SalaryPayment.objects.get(pk=1)
        original = salary_payment.week_end
        salary_payment.week_end = datetime.date.today()\
                                  - datetime.timedelta(days = 2)
        salary_payment.save()
        salary_payment.refresh_from_db()
        self.assertEqual(salary_payment.week_end, original)

    def test_clean_week_start(self):
        with self.assertRaises(ValidationError) as cm:
            salary_payment =  SalaryPayment.objects.get(pk=1)
            salary_payment.week_start = None
            salary_payment.full_clean()
        
        exception = cm.exception
        self.assertTrue('week_start' in exception.error_dict.keys())

    def test_clean_week_end(self):
        with self.assertRaises(ValidationError) as cm:
            salary_payment =  SalaryPayment.objects.get(pk=1)
            salary_payment.week_end = None
            salary_payment.full_clean()
        
        exception = cm.exception
        self.assertTrue('week_end' in exception.error_dict.keys())

    def test_clean_user(self):
        with self.assertRaises(ValidationError) as cm:
            salary_payment =  SalaryPayment.objects.get(pk=1)
            salary_payment.user = None
            salary_payment.full_clean()
        
        exception = cm.exception
        self.assertTrue('user' in exception.error_dict.keys())

    def test_clean_user_not_regional_manager(self):
        user = CustomUser.objects.create(
            username='matt', password='Ilovemeatballs')
        with self.assertRaises(ValidationError) as cm:
            salary_payment =  SalaryPayment.objects.get(pk=1)
            salary_payment.user = user
            salary_payment.full_clean()
        
        exception = cm.exception
        self.assertEqual(
            exception.messages,
                ['Assign a user that is salaried.'])

    def test_clean_dates_more_than_seven_days(self):
        with self.assertRaises(ValidationError) as cm:
            salary_payment =  SalaryPayment.objects.get(pk=1)
            salary_payment.week_start = datetime.date.today()\
                                        - datetime.timedelta(days=8)
            salary_payment.week_end = datetime.date.today()
            salary_payment.full_clean()
        
        exception = cm.exception
        self.assertEqual(
            exception.message_dict,
                {
                    '__all__': ['Week start and week end must '
                               'be no more than 7 days apart.'],
                    'week_start': [''],
                    'week_end': ['']
                }
            )

    def test_clean_week_end_earlier_than_week_start(self):
        with self.assertRaises(ValidationError) as cm:
            salary_payment =  SalaryPayment.objects.get(pk=1)
            salary_payment.week_start = datetime.date.today()
            salary_payment.week_end = datetime.date.today()\
                                      - datetime.timedelta(days=8)
            salary_payment.full_clean()
        
        exception = cm.exception
        self.assertEqual(
            exception.message_dict,
                {
                    '__all__': [('Week start must be before week end')],
                    'week_start': [''],
                    'week_end': ['']
                }
            )

class EventOccurrencePaymentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti',
            is_regional_manager=True)
        host_profile = HostProfile.objects.create(
            user = user,
            base_teams=5, base_rate=50,
            incremental_teams=1, incremental_rate=1 
            )
        day = Day.objects.create(day=datetime.date.today().weekday())
        event = Event.objects.create(
            day=day,
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=28))
        event_occurrence = EventOccurrence.objects.create(
            event=event,
            host=user,
            status='Game',
            time_started=datetime.time(20,30),
            time_ended=datetime.time(22,30),
            number_of_teams=5)

    def test_type_label(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        field_label = occurrence_payment._meta.get_field('type').verbose_name
        self.assertEqual(field_label, 'type')

    def test_type_max_length(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        max_length = occurrence_payment._meta.get_field('type').max_length
        self.assertEqual(max_length, 1)

    def test_type_default(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        default = occurrence_payment._meta.get_field('type').default
        self.assertEqual(default, "R")
        
    def test_type_choices(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        field_choices = occurrence_payment._meta.get_field('type').choices
        expected_value = ['R', 'P']
        expected_human_readable = ['Regular Event', 'Private Event']
        for index, (value, human_readable) in enumerate(field_choices):
            self.assertEqual(value, expected_value[index])
            self.assertEqual(human_readable, expected_human_readable[index])

    def test_type_blank(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        blank = occurrence_payment._meta.get_field('type').blank
        self.assertEqual(blank, True)

    def test_submission_date_label(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        field_label = occurrence_payment._meta.get_field('submission_date').verbose_name
        self.assertEqual(field_label, 'submission date')

    def test_submission_date_null(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        null = occurrence_payment._meta.get_field('submission_date').null
        self.assertEqual(null, True)

    def test_submission_date_blank(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        blank = occurrence_payment._meta.get_field('submission_date').blank
        self.assertEqual(blank, True)

    def test_event_occurrence_label(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        field_label = occurrence_payment._meta.get_field('event_occurrence').verbose_name
        self.assertEqual(field_label, 'event occurrence')

    def test_event_occurrence_class(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        model = occurrence_payment._meta.get_field('event_occurrence').related_model
        self.assertEqual(model, EventOccurrence)

    def test_event_occurrence_on_delete_set_null(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        event_occurrence = occurrence_payment.event_occurrence
        event_occurrence.delete()
        occurrence_payment.refresh_from_db()
        event_occurrence = occurrence_payment.event_occurrence
        event_occurrence_count = EventOccurrence.objects.all().count()
        payment_count = EventOccurrencePayment.objects.all().count()
        self.assertEqual(event_occurrence, None)
        self.assertEqual(event_occurrence_count, 0)
        self.assertEqual(payment_count, 1)

    def test_event_occurrence_null(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        null = occurrence_payment._meta.get_field('event_occurrence').null
        self.assertEqual(null, True)

    def test_event_occurrence_blank(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        blank = occurrence_payment._meta.get_field('event_occurrence').blank
        self.assertEqual(blank, True)

    def test_event_occurence_related_name_is_event_occurrance_payments(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        related_name = occurrence_payment.event_occurrence._meta.get_field(
            'event_occurrence_payments').related_name
        self.assertEqual(related_name, 'event_occurrence_payments')
        
    def test_gross_amount_label(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        field_label = occurrence_payment._meta.get_field('gross_amount').verbose_name
        self.assertEqual(field_label, 'gross amount')

    def test_gross_amount_max_digits(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        max_digits = occurrence_payment._meta.get_field('gross_amount').max_digits
        self.assertEqual(max_digits, 5)

    def test_gross_amount_decimal_places(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        decimal_places = occurrence_payment._meta.get_field('gross_amount').decimal_places
        self.assertEqual(decimal_places, 2)

    def test_gross_amount_null(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        null = occurrence_payment._meta.get_field('gross_amount').null
        self.assertEqual(null, True)

    def test_gross_amount_blank(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        blank = occurrence_payment._meta.get_field('gross_amount').blank
        self.assertEqual(blank, True)

    def test_paid_label(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        field_label = occurrence_payment._meta.get_field('paid').verbose_name
        self.assertEqual(field_label, 'paid')

    def test_paid_default(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        default = occurrence_payment._meta.get_field('paid').default
        self.assertEqual(default, False)
        
    def test_pay_stub_label(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        field_label = occurrence_payment._meta.get_field('pay_stub').verbose_name
        self.assertEqual(field_label, 'pay stub')

    def test_pay_stub_class(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        model = occurrence_payment._meta.get_field('pay_stub').related_model
        self.assertEqual(model, PayStub)

    def test_pay_stub_null_on_delete(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        pay_stub = occurrence_payment.pay_stub
        pay_stub.delete()
        pay_stub_count = PayStub.objects.all().count()
        occurrence_payment_count = EventOccurrencePayment.objects.all().count()
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        self.assertEqual(pay_stub_count, 0)
        self.assertEqual(occurrence_payment_count, 1)
        self.assertEqual(occurrence_payment.pay_stub, None)

    def test_pay_stub_null(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        null = occurrence_payment._meta.get_field('pay_stub').null
        self.assertEqual(null, True)

    def test_pay_stub_blank(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        blank = occurrence_payment._meta.get_field('pay_stub').blank
        self.assertEqual(blank, True)

    def test_pay_stub_related_name_is_salary_payments(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        related_name = occurrence_payment.pay_stub._meta.get_field('event_occurrence_payments').related_name
        self.assertEqual(related_name, 'event_occurrence_payments')

    def test_str_(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        self.assertEqual(
            str(occurrence_payment),
            '{0} {1} {2} {3}'.format(
            occurrence_payment.type,
            occurrence_payment.submission_date,
            occurrence_payment.event_occurrence,
            occurrence_payment.gross_amount))

    def test_save_not_paid_updated_number_of_teams_updates_amount_and_submission_date(self):
        query = EventOccurrencePayment.objects.filter(pk=1)
        query.update(submission_date=datetime.date.today() - datetime.timedelta(days=1))
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        original_submission = occurrence_payment.submission_date
        original = occurrence_payment.gross_amount
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.number_of_teams = 20
        occurrence.save()
        occurrence_payment.refresh_from_db()
        self.assertNotEqual(occurrence_payment.gross_amount, original)
        self.assertNotEqual(occurrence_payment.submission_date, original_submission)

    def test_save_edited_occurrence_payment_reverts_to_event_occurrence_payment_calculation(self):
        query = EventOccurrencePayment.objects.filter(pk=1)
        query.update(submission_date=datetime.date.today() - datetime.timedelta(days=1))
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        original_submission = occurrence_payment.submission_date
        original = occurrence_payment.gross_amount
        occurrence_payment.gross_amount = 100
        occurrence_payment.save()
        occurrence_payment.refresh_from_db()
        self.assertEqual(occurrence_payment.gross_amount, original)
        self.assertEqual(occurrence_payment.submission_date, original_submission)

    def test_save_not_paid_unedited_leaves_submission_date_same(self):
        query = EventOccurrencePayment.objects.filter(pk=1)
        query.update(submission_date=datetime.date.today() - datetime.timedelta(days=1))
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        original_submission = occurrence_payment.submission_date
        original = occurrence_payment.gross_amount
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.number_of_teams = 5
        occurrence.save()
        occurrence_payment.refresh_from_db()
        self.assertEqual(occurrence_payment.gross_amount, original)
        self.assertEqual(occurrence_payment.submission_date, original_submission)

    def test_clean_private_event_assigns_payment_as_private_event_pay_and_payment_type_p(self):
        occurrence = EventOccurrence.objects.get(pk=1)
        occurrence.event.is_private = True
        occurrence.event.save()
        occurrence.save()
        occurrence_payment = EventOccurrencePayment.objects.get(event_occurrence=occurrence)
        self.assertEqual(occurrence_payment.gross_amount, 150)
        self.assertEqual(occurrence_payment.type, 'P')

    def test_clean_event_occurrence(self):
        with self.assertRaises(ValidationError) as cm:
            occurrence_payment =  EventOccurrencePayment.objects.get(pk=1)
            occurrence_payment.event_occurrence = None
            occurrence_payment.full_clean()
        
        exception = cm.exception
        self.assertEqual(
            exception.message_dict,
                {
                    'event_occurrence': [('')],
                }
            )

    def test_calculate_pay(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        occurrence_payment.event_occurrence.number_of_teams = 10
        occurrence_payment.event_occurrence.save()
        occurrence_payment.calculate_pay()
        self.assertEqual(occurrence_payment.gross_amount, 50+(10-5)*1)

    def test_display_event_date(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        self.assertEqual(
            occurrence_payment.display_event_date(),
            occurrence_payment.event_occurrence.date)

    def test_display_event(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        self.assertEqual(
            occurrence_payment.display_event(),
            occurrence_payment.event_occurrence.event)

    def test_display_host(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        self.assertEqual(
            occurrence_payment.display_host(),
            occurrence_payment.event_occurrence.host)

    def test_display_number_of_teams(self):
        occurrence_payment = EventOccurrencePayment.objects.get(pk=1)
        self.assertEqual(
            occurrence_payment.display_number_of_teams(),
            occurrence_payment.event_occurrence.number_of_teams)

@override_settings(MEDIA_ROOT='temp_reimbursement_docs')
class ReimbursementModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti',
            is_regional_manager=True)
        test_file = SimpleUploadedFile('test_file.txt', b'test file text')
        reimbursement = Reimbursement.objects.create(
            user=user,
            purchase_date=datetime.date.today(),
            documentation=test_file)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('temp_reimbursement_docs')
        super().tearDownClass()
        
    def test_submission_date_label(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        field_label = reimbursement._meta.get_field('submission_date').verbose_name
        self.assertEqual(field_label, 'submission date')

    def test_submission_date_null(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        null = reimbursement._meta.get_field('submission_date').null
        self.assertEqual(null, True)

    def test_submission_date_blank(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        blank = reimbursement._meta.get_field('submission_date').blank
        self.assertEqual(blank, True)

    def test_purchase_date_label(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        field_label = reimbursement._meta.get_field('purchase_date').verbose_name
        self.assertEqual(field_label, 'purchase date')

    def test_purchase_date_null(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        null = reimbursement._meta.get_field('purchase_date').null
        self.assertEqual(null, True)

    def test_purchase_date_blank(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        blank = reimbursement._meta.get_field('purchase_date').blank
        self.assertEqual(blank, True)

    def test_category_choices(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        field_choices = reimbursement._meta.get_field('category').choices
        expected_value = ['F/D', 'GS', 'E', 'T']
        expected_human_readable = ['Food or Drink', 'Game Supplies',
                                  'Equipment', 'Transportation']
        for index, (value, human_readable) in enumerate(field_choices):
            self.assertEqual(value, expected_value[index])
            self.assertEqual(human_readable, expected_human_readable[index])

    def test_category_label(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        field_label = reimbursement._meta.get_field('category').verbose_name
        self.assertEqual(field_label, 'category')

    def test_category_max_length(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        max_length = reimbursement._meta.get_field('category').max_length
        self.assertEqual(max_length, 20)

    def test_category_choices(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        choices = reimbursement._meta.get_field('category').choices
        self.assertEqual(choices, Reimbursement.CATEGORY)

    def test_category_blank(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        blank = reimbursement._meta.get_field('category').blank
        self.assertEqual(blank, True)

    def test_description_label(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        field_label = reimbursement._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'description')

    def test_description_blank(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        blank = reimbursement._meta.get_field('description').blank
        self.assertEqual(blank, True)

    def test_amount_label(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        field_label = reimbursement._meta.get_field('amount').verbose_name
        self.assertEqual(field_label, 'amount')

    def test_amount_max_digits(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        max_digits = reimbursement._meta.get_field('amount').max_digits
        self.assertEqual(max_digits, 5)

    def test_amount_decimal_places(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        decimal_places = reimbursement._meta.get_field('amount').decimal_places
        self.assertEqual(decimal_places, 2)

    def test_amount_null(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        null = reimbursement._meta.get_field('amount').null
        self.assertEqual(null, True)

    def test_amount_blank(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        blank = reimbursement._meta.get_field('amount').blank
        self.assertEqual(blank, True)

    def test_cancellation_reason_help_text(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        help_text = reimbursement._meta.get_field('amount').help_text
        self.assertEqual(
            help_text, 'Only enter amount. Do not add "$". Example, 2.25.')

    def test_document_uploads_to_reimbursements_username_date_filename(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        filename = 'test_file.txt'
        folder = 'reimbursements'
        sub_folder = str(reimbursement.user.username)
        purchase_date = reimbursement.purchase_date
        self.assertEqual(
            reimbursement.documentation.name,
            '{0}/{1}/{2}_{3}'.format(folder, sub_folder, purchase_date, filename))

    def test_user_label(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        field_label = reimbursement._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_reimbursement_class(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        model = reimbursement._meta.get_field('user').related_model
        self.assertEqual(model, CustomUser)

    def test_user_null_on_delete(self):
        user = CustomUser.objects.get(pk=1)
        user.delete()
        user_count = CustomUser.objects.all().count()
        reimbursement_count = Reimbursement.objects.all().count()
        reimbursement = Reimbursement.objects.get(pk=1)
        self.assertEqual(user_count, 0)
        self.assertEqual(reimbursement_count, 1)
        self.assertEqual(reimbursement.user, None)

    def test_user_null(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        null = reimbursement._meta.get_field('user').null
        self.assertEqual(null, True)

    def test_user_blank(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        blank = reimbursement._meta.get_field('user').blank
        self.assertEqual(blank, True)

    def test_user_related_name_is_reimbursements(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        related_name = reimbursement.user._meta.get_field('reimbursements').related_name
        self.assertEqual(related_name, 'reimbursements')

    def test_pay_stub_label(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        field_label = reimbursement._meta.get_field('pay_stub').verbose_name
        self.assertEqual(field_label, 'pay stub')

    def test_pay_stub_class(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        model = reimbursement._meta.get_field('pay_stub').related_model
        self.assertEqual(model, PayStub)

    def test_pay_stub_null_on_delete(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        reimbursement.approved = True
        reimbursement.approved_amount = 2.50
        reimbursement.save()
        pay_stub = PayStub.objects.get(pk=1)
        pay_stub.delete()
        pay_stub_count = PayStub.objects.all().count()
        reimbursement_count = Reimbursement.objects.all().count()
        reimbursement = Reimbursement.objects.get(pk=1)
        self.assertEqual(pay_stub_count, 0)
        self.assertEqual(reimbursement_count, 1)
        self.assertEqual(reimbursement.pay_stub, None)

    def test_pay_stub_null(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        null = reimbursement._meta.get_field('pay_stub').null
        self.assertEqual(null, True)

    def test_pay_stub_blank(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        blank = reimbursement._meta.get_field('pay_stub').blank
        self.assertEqual(blank, True)

    def test_pay_stub_related_name_is_reimbursements(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        reimbursement.approved = True
        reimbursement.approved_amount = 2.50
        reimbursement.save()
        related_name = reimbursement.pay_stub._meta.get_field('reimbursements').related_name
        self.assertEqual(related_name, 'reimbursements')

    def test_approved_label(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        field_label = reimbursement._meta.get_field('approved').verbose_name
        self.assertEqual(field_label, 'approved')

    def test_approved_default(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        default = reimbursement._meta.get_field('approved').default
        self.assertEqual(default, False)

    def test_approved_amount_label(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        field_label = reimbursement._meta.get_field('approved_amount').verbose_name
        self.assertEqual(field_label, 'approved amount')

    def test_approved_amount_max_digits(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        max_digits = reimbursement._meta.get_field('approved_amount').max_digits
        self.assertEqual(max_digits, 5)

    def test_approved_amount_decimal_places(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        decimal_places = reimbursement._meta.get_field('approved_amount').decimal_places
        self.assertEqual(decimal_places, 2)

    def test_approved_amount_null(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        null = reimbursement._meta.get_field('approved_amount').null
        self.assertEqual(null, True)

    def test_approved_amount_blank(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        blank = reimbursement._meta.get_field('approved_amount').blank
        self.assertEqual(blank, True)

    def test_paid_label(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        field_label = reimbursement._meta.get_field('paid').verbose_name
        self.assertEqual(field_label, 'paid')

    def test_paid_default(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        default = reimbursement._meta.get_field('paid').default
        self.assertEqual(default, False)

    def test_str(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        self.assertEqual(
            str(reimbursement),
            '{0}: {1} - {2}'.format(
                reimbursement.purchase_date,
                reimbursement.category,
                reimbursement.amount))

    def test_save_new_reimbursement(self):
        reimbursement = Reimbursement.objects.create()
        self.assertEqual(reimbursement.submission_date, datetime.date.today())

    def test_save_edited_reimbursement_category_updates_submission_date(self):
        query = Reimbursement.objects.filter(pk=1)
        query.update(submission_date=datetime.date.today()-datetime.timedelta(days=1))
        reimbursement = Reimbursement.objects.get(pk=1)
        original = reimbursement.submission_date
        reimbursement.category = 'GS'
        reimbursement.save()
        reimbursement.refresh_from_db()
        self.assertNotEqual(reimbursement.submission_date, original)

    def test_save_edited_reimbursement_purchase_date_updates_submission_date(self):
        query = Reimbursement.objects.filter(pk=1)
        query.update(submission_date=datetime.date.today()-datetime.timedelta(days=1))
        reimbursement = Reimbursement.objects.get(pk=1)
        original = reimbursement.submission_date
        reimbursement.purchase_date = datetime.date.today()-datetime.timedelta(days=1)
        reimbursement.save()
        reimbursement.refresh_from_db()
        self.assertNotEqual(reimbursement.submission_date, original)

    def test_save_edited_reimbursement_category_updates_submission_date(self):
        query = Reimbursement.objects.filter(pk=1)
        query.update(submission_date=datetime.date.today()-datetime.timedelta(days=1))
        reimbursement = Reimbursement.objects.get(pk=1)
        original = reimbursement.submission_date
        reimbursement.category = 'GS'
        reimbursement.save()
        reimbursement.refresh_from_db()
        self.assertNotEqual(reimbursement.submission_date, original)

    def test_save_edited_reimbursement_description_updates_submission_date(self):
        query = Reimbursement.objects.filter(pk=1)
        query.update(submission_date=datetime.date.today()-datetime.timedelta(days=1))
        reimbursement = Reimbursement.objects.get(pk=1)
        original = reimbursement.submission_date
        reimbursement.description = 'Bought some drinks'
        reimbursement.save()
        reimbursement.refresh_from_db()
        self.assertNotEqual(reimbursement.submission_date, original)

    def test_save_edited_reimbursement_amount_updates_submission_date(self):
        query = Reimbursement.objects.filter(pk=1)
        query.update(submission_date=datetime.date.today()-datetime.timedelta(days=1))
        reimbursement = Reimbursement.objects.get(pk=1)
        original = reimbursement.submission_date
        reimbursement.amount = '5.00'
        reimbursement.save()
        reimbursement.refresh_from_db()
        self.assertNotEqual(reimbursement.submission_date, original)

    def test_save_if_approved_assign_pay_stub_and_add_amount_to_paystub(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        pay_stub_before = reimbursement.pay_stub
        reimbursement.approved = True
        reimbursement.approved_amount = 2.50
        reimbursement.save()
        reimbursement.refresh_from_db()
        pay_stub_after = reimbursement.pay_stub
        self.assertFalse(pay_stub_before)
        self.assertTrue(pay_stub_after)
        self.assertEqual(
            reimbursement.pay_stub.total_reimbursement_amount,
            2.50)

    def test_save_if_edited_requires_approval_clears_approved_amount_and_updates_pay_stub(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        reimbursement.approved = True
        reimbursement.approved_amount = 2.50
        reimbursement.save()
        reimbursement.refresh_from_db()
        original = reimbursement.pay_stub
        reimbursement.amount = 5.00
        reimbursement.save()
        reimbursement.refresh_from_db()
        self.assertFalse(reimbursement.approved)
        self.assertFalse(reimbursement.approved_amount)
        self.assertFalse(reimbursement.pay_stub)

    def test_save_paid_can_not_edit(self):
        reimbursement = Reimbursement.objects.get(pk=1)
        reimbursement.approved = True
        reimbursement.approved_amount = 2.50
        reimbursement.save()
        reimbursement.refresh_from_db()
        reimbursement.pay_stub.paid = True
        reimbursement.pay_stub.save()
        reimbursement.refresh_from_db()
        original = reimbursement.approved_amount
        reimbursement.approve_amount = 500
        reimbursement.save()
        reimbursement.refresh_from_db()
        self.assertEqual(reimbursement.approved_amount, original)

    def test_clean_no_approved_amount(self):
        with self.assertRaises(ValidationError) as cm:
            reimbursement =  Reimbursement.objects.get(pk=1)
            reimbursement.approved = True
            reimbursement.full_clean()
        
        exception = cm.exception
        self.assertTrue('approved_amount' in exception.error_dict.keys())