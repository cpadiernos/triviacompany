from django.forms.widgets import FileInput
from django.forms.fields import CharField
from django.shortcuts import reverse
from django.test import TestCase

from accounts.models import CustomUser
from accounts.forms import CustomUserUpdateForm
from locations.models import City, State, Zip

from localflavor.us.forms import USStateField, USZipCodeField

class CustomUserUpdateFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti',
            is_host=True)

    def test_custom_user_update_form_meta(self):
        self.assertEqual(CustomUser, CustomUserUpdateForm.Meta.model)
        self.assertEqual(
            ('first_name', 'last_name', 'email',
            'secondary_email', 'mobile_number', 'work_number', 
            'mailing_address', 'mailing_additional_address',
            'mailing_city', 'mailing_state', 'mailing_zip',
            'profile_image'),
            CustomUserUpdateForm.Meta.fields)
        self.assertIsInstance(CustomUserUpdateForm.Meta.widgets.get('profile_image'), FileInput)
        
    def test_custom_user_update_form_mailing_city_field(self):
        field = CustomUserUpdateForm.declared_fields.get('mailing_city')
        self.assertIsInstance(field, CharField)
        self.assertEqual(field.max_length, 200)
        self.assertEqual(field.required, False)

    def test_custom_user_update_form_mailing_state_field(self):
        field = CustomUserUpdateForm.declared_fields.get('mailing_state')
        self.assertIsInstance(field, USStateField)
        self.assertTrue(any('' in choice for choice in field.widget.choices))
        self.assertEqual(field.required, False)
    
    def test_custom_user_update_form_mailing_zip_field(self):
        field = CustomUserUpdateForm.declared_fields.get('mailing_zip')
        self.assertIsInstance(field, USZipCodeField)
        self.assertEqual(field.required, False)

    def test_custom_user_update_form_TEST_TEST(self):
        user = CustomUser.objects.get(username='carol')
        state = State.objects.create(name='NY')
        city = City.objects.create(name='Cat City', state=state)
        zip = Zip.objects.create(code='11111', city=city)
        user.mailing_state = state
        user.mailing_city = city
        user.mailing_zip = zip
        user.save()
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('account-update', kwargs={'username': 'carol'})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertEqual(form.initial.get('mailing_state'), state.name)
        self.assertEqual(form.initial.get('mailing_city'), city.name)
        self.assertEqual(form.initial.get('mailing_zip'), zip.code)

    def test_custom_user_update_form_invalid_post_data_address_only(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('account-update', kwargs={'username': 'carol'})
        data = {
            'mailing_address': '1 Orange Cat Way'
        }
        response = self.client.post(url, data)
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form.errors['mailing_city'], ['Please provide the full address.'])
        self.assertEqual(form.errors['mailing_state'], ['Please provide the full address.'])
        self.assertEqual(form.errors['mailing_zip'], ['Please provide the full address.'])
        self.assertEqual(form.errors['__all__'], ['Please correct the error below.'])
        
    def test_custom_user_update_form_invalid_post_data_mailing_city_only(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('account-update', kwargs={'username': 'carol'})
        data = {
            'mailing_city': 'Catville'
        }
        response = self.client.post(url, data)
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form.errors['__all__'], ['Please correct the error below.'])
        self.assertEqual(form.errors['mailing_address'], ['Please provide the full address.'])
        self.assertEqual(form.errors['mailing_state'], ['Please provide the full address.'])
        self.assertEqual(form.errors['mailing_zip'], ['Please provide the full address.'])
        
    def test_custom_user_update_form_invalid_post_data_mailing_state_only(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('account-update', kwargs={'username': 'carol'})
        data = {
            'mailing_state': 'NJ',
        }
        response = self.client.post(url, data)
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form.errors['__all__'], ['Please correct the error below.'])
        self.assertEqual(form.errors['mailing_address'], ['Please provide the full address.'])
        self.assertEqual(form.errors['mailing_city'], ['Please provide the full address.'])
        self.assertEqual(form.errors['mailing_zip'], ['Please provide the full address.'])
        
    def test_custom_user_update_form_invalid_post_data_mailing_zip_only(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('account-update', kwargs={'username': 'carol'})
        data = {
            'mailing_zip': '07302',
        }
        response = self.client.post(url, data)
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form.errors['__all__'], ['Please correct the error below.'])
        self.assertEqual(form.errors['mailing_address'], ['Please provide the full address.'])
        self.assertEqual(form.errors['mailing_city'], ['Please provide the full address.'])
        self.assertEqual(form.errors['mailing_state'], ['Please provide the full address.'])
        
    def test_custom_user_update_form_valid_post_data_no_data(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('account-update', kwargs={'username': 'carol'})
        data = {}
        response = self.client.post(url, data, follow=True)
        user = CustomUser.objects.get(username='carol')
        self.assertContains(response, 'Your account has been updated!')
        self.assertEqual(user.mailing_address, '')
        self.assertEqual(user.mailing_city, None)
        self.assertEqual(user.mailing_state, None)
        self.assertEqual(user.mailing_zip, None)
        
    def test_custom_user_update_form_valid_post_data_full_address(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('account-update', kwargs={'username': 'carol'})
        data = {
            'mailing_address': '1 Orange Kitty Way',
            'mailing_city': 'Catville',
            'mailing_state': 'NJ',
            'mailing_zip': '07302',
        }
        response = self.client.post(url, data, follow=True)
        user = CustomUser.objects.get(username='carol')
        state = State.objects.get(name='NJ')
        city = City.objects.get(name='Catville', state=state)
        zip = Zip.objects.get(code='07302', city=city)
        self.assertContains(response, 'Your account has been updated!')
        self.assertEqual(user.mailing_address,'1 Orange Kitty Way')
        self.assertEqual(user.mailing_city, city)
        self.assertEqual(user.mailing_state, state)
        self.assertEqual(user.mailing_zip, zip)