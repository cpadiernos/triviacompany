import datetime

from django.forms.widgets import DateInput
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from accounting.models import Reimbursement
from accounting.forms import ReimbursementForm
from accounts.models import CustomUser

class ReimbursementFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')

    def test_reimbursement_form_meta(self):
        self.assertEqual(Reimbursement, ReimbursementForm.Meta.model)
        self.assertEqual((
            'purchase_date', 'category', 'description', 'amount',
            'documentation'),
            ReimbursementForm.Meta.fields)

    def test_reimbursement_form_valid_post_data(self):
        test_file = SimpleUploadedFile('documentation.txt', b'Beer $4.50.')
        data = {
            'purchase_date': datetime.date.today(),
            'category': 'F/D',
            'description': 'Beer for disgruntled player.',
            'amount': '4.50',
        }
        files = {
            'documentation': test_file,
        }
        form = ReimbursementForm(data, files)
        self.assertTrue(form.is_valid())
        
    def test_reimbursement_form_invalid_post_data(self):
        data = {
            'purchase_date': '',
            'category': '',
            'description': '',
            'amount': '',
        }
        files = {
            'documentation': '',
        }
        form = ReimbursementForm(data, files)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['purchase_date'], ['This field is required.'])
        self.assertEqual(
            form.errors['category'], ['This field is required.'])
        self.assertEqual(
            form.errors['description'], ['This field is required.'])
        self.assertEqual(
            form.errors['amount'], ['This field is required.'])
        self.assertEqual(
            form.errors['documentation'], ['This field is required.'])