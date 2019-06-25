from django.test import TestCase
from django.urls import reverse, resolve
from accounts.models import CustomUser
from policies.models import Policy, Section
from policies.views import (
    PolicyListView,
    PolicyCreate,
    PolicyUpdate,
    PolicyDelete,
    SectionCreate,
    SectionUpdate,
    SectionDelete,
    SectionMove,
)

class PolicyListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        host = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti',
            is_host=True)
        policy = Policy.objects.create(
            name='Dog Care',
            detail='This policy handles all aspects of dog care.')
        section = Section.objects.create(
            policy=policy,
            name='Training',
            detail='Training your dog takes patience and a lot of repetition.')

    def test_policies_url_maps_to_policy_list_name(self):
        url = '/policies/'
        reversed_name = reverse('policy-list')
        self.assertEqual(url, reversed_name)

    def test_reverse_policy_list_name_resolves_to_policy_list_view_view(self):
        view = resolve(reverse('policy-list'))
        self.assertEqual(view.func.view_class, PolicyListView)

    def test_reverse_policy_list_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'policies/policy_list.html')

    def test_reverse_policy_list_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('policy-list')
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_policy_list_name_success_status_code_if_logged_in_as_host(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_policy_list_name_success_status_code_if_logged_in_as_regional_manager(self):
        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = True
        user.save()
        
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_policy_list_name_forbidden_status_code_if_logged_in_as_other_than_host_or_regional_manager(self):
        user = CustomUser.objects.get(username='carol')
        user.is_host = False
        user.is_regional_manager = False
        user.save()

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_reverse_policy_list_name_redirects_to_current_page_after_logging_in(self):
        url = reverse('policy-list')
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)

    # test_templates?
    def test_reverse_policy_list_name_contains_link_to_policy_create_name_if_user_is_regional_manager(self):
        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = True
        user.save()

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        policy_create_url = reverse('policy-create')
        self.assertContains(response, 'href="{0}"'.format(policy_create_url))

    def test_reverse_policy_list_name_does_not_contain_link_to_policy_create_name_if_user_is_not_regional_manager(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        policy_create_url = reverse('policy-create')
        self.assertNotContains(response, 'href="{0}"'.format(policy_create_url))

    def test_reverse_policy_list_name_contains_link_to_policy_update_name_if_user_is_regional_manager(self):
        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = True
        user.save()

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        policy_update_url = reverse('policy-update', kwargs={'pk': 1})
        self.assertContains(response, 'href="{0}"'.format(policy_update_url))

    def test_reverse_policy_list_name_does_not_contain_link_to_policy_update_name_if_user_is_not_regional_manager(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        policy_update_url = reverse('policy-update', kwargs={'pk': 1})
        self.assertNotContains(response, 'href="{0}"'.format(policy_update_url))

    def test_reverse_policy_list_name_contains_link_to_policy_delete_name_if_user_is_regional_manager(self):
        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = True
        user.save()

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        policy_delete_url = reverse('policy-delete', kwargs={'pk': 1})
        self.assertContains(response, 'href="{0}"'.format(policy_delete_url))

    def test_reverse_policy_list_name_does_not_contain_link_to_policy_delete_name_if_user_is_not_regional_manager(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        policy_delete_url = reverse('policy-delete', kwargs={'pk': 1})
        self.assertNotContains(response, 'href="{0}"'.format(policy_delete_url))

    def test_reverse_policy_list_name_contains_link_to_section_create_name_if_user_is_regional_manager(self):
        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = True
        user.save()

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        section_create_url = reverse('section-create', kwargs={'pk': 1})
        self.assertContains(response, 'href="{0}"'.format(section_create_url))

    def test_reverse_policy_list_name_does_not_contain_link_to_section_create_name_if_user_is_not_regional_manager(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        section_create_url = reverse('section-create', kwargs={'pk': 1})
        self.assertNotContains(response, 'href="{0}"'.format(section_create_url))

    def test_reverse_policy_list_name_contains_link_to_section_update_name_if_user_is_regional_manager(self):
        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = True
        user.save()

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        section_update_url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        self.assertContains(response, 'href="{0}"'.format(section_update_url))

    def test_reverse_policy_list_name_does_not_contain_link_to_section_update_name_if_user_is_not_regional_manager(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        section_update_url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        self.assertNotContains(response, 'href="{0}"'.format(section_update_url))

    def test_reverse_policy_list_name_contains_link_to_section_delete_name_if_user_is_regional_manager(self):
        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = True
        user.save()

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        section_delete_url = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 1})
        self.assertContains(response, 'href="{0}"'.format(section_delete_url))

    def test_reverse_policy_list_name_does_not_contain_link_to_section_delete_name_if_user_is_not_regional_manager(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        section_delete_url = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 1})
        self.assertNotContains(response, 'href="{0}"'.format(section_delete_url))

    def test_reverse_policy_list_name_contains_link_to_section_move_name_if_user_is_regional_manager(self):
        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = True
        user.save()

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        section_move_url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        self.assertContains(response, 'href="{0}"'.format(section_move_url))

    def test_reverse_policy_list_name_does_not_contain_link_to_section_move_name_if_user_is_not_regional_manager(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-list')
        response = self.client.get(url)
        section_move_url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        self.assertNotContains(response, 'href="{0}"'.format(section_move_url))

class PolicyCreateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti',
            is_regional_manager=True)

    def test_policies_new_url_maps_to_policy_create_name(self):
        url = '/policies/new/'
        reversed_name = reverse('policy-create')
        self.assertEqual(url, reversed_name)

    def test_reverse_policy_create_name_resolves_to_policy_create_view(self):
        view = resolve(reverse('policy-create'))
        self.assertEqual(view.func.view_class, PolicyCreate)

    def test_reverse_policy_create_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-create')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'policies/policy_form.html')

    def test_reverse_policy_create_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('policy-create')
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_policy_create_name_success_status_code_if_logged_in_as_regional_manager(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_policy_create_name_forbidden_status_code_if_logged_in_as_other_than_regional_manager(self):
        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = False
        user.save()

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_reverse_policy_create_name_redirects_to_current_page_after_logging_in_as_regional_manager(self):
        url = reverse('policy-create')
        response_before_login = self.client.get(url)
        login_url = response_before_login.url

        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = True
        user.save()

        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)

    def test_reverse_policy_create_name_form_csrf(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-create')
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_reverse_policy_create_name_valid_post_data(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-create')
        data = {
            'name': 'Cat Care',
            'detail': 'This policy handles all aspects of cat care.'
        }
        response = self.client.post(url, data)
        self.assertEqual(Policy.objects.all().count(), 1)

    def test_reverse_policy_create_name_redirects_to_policy_list_name_after_valid_post(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-create')
        data = {
            'name': 'Cat Care',
            'detail': 'This policy handles all aspects of cat care.'
        }
        response = self.client.post(url, data)
        success_url = reverse('policy-list')
        self.assertRedirects(response, success_url)

    def test_reverse_policy_create_name_invalid_post_data_returns_with_name_is_required_error(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-create')
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form.errors['name'], ['This field is required.'])

    def test_reverse_policy_create_name_invalid_post_data_empty_fields(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-create')
        data = {
            'name': '',
            'detail': ''
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Policy.objects.all().count(), 0)

class PolicyUpdateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti',
            is_regional_manager=True)
        policy = Policy.objects.create(
            name='Dog Care',
            detail='This policy handles all aspects of dog care.')

    def test_policies_pk_update_url_maps_to_policy_update_name(self):
        url = '/policies/1/update/'
        reversed_name = reverse('policy-update', kwargs={'pk': 1})
        self.assertEqual(url, reversed_name)

    def test_reverse_policy_update_name_resolves_to_policy_update_view(self):
        view = resolve(reverse('policy-update', kwargs={'pk': 1}))
        self.assertEqual(view.func.view_class, PolicyUpdate)

    def test_reverse_policy_update_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'policies/policy_form.html')

    def test_reverse_policy_update_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('policy-update', kwargs={'pk': 1})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_policy_update_name_success_status_code_if_logged_in_as_regional_manager(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_policy_update_name_not_found_status_code(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-update', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_policy_update_name_forbidden_status_code_if_logged_in_as_other_than_regional_manager(self):
        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = False
        user.save()

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_reverse_policy_update_name_redirects_to_current_page_after_logging_in_as_regional_manager(self):
        url = reverse('policy-update', kwargs={'pk': 1})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url

        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = True
        user.save()
        
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)

    def test_reverse_policy_update_name_form_csrf(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_reverse_policy_update_name_valid_post_data(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-update', kwargs={'pk': 1})
        data = {
            'name': 'Dog Care and Behavior',
            'detail': 'This policy handles all aspects of dog care and behavior.'
        }
        response = self.client.post(url, data)
        policy = Policy.objects.get(pk=1)
        self.assertEqual(policy.name, 'Dog Care and Behavior')
        self.assertEqual(policy.detail, 'This policy handles all aspects of dog care and behavior.')
        self.assertEqual(Policy.objects.all().count(), 1)

    def test_reverse_policy_update_name_redirects_to_policy_list_name_after_valid_post(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-update', kwargs={'pk': 1})
        data = {
            'name': 'Dog Care and Behavior',
            'detail': 'This policy handles all aspects of dog care and behavior.'
        }
        response = self.client.post(url, data)
        success_url = reverse('policy-list')
        self.assertRedirects(response, success_url)

    def test_reverse_policy_update_name_invalid_post_data_returns_with_name_is_required_error(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-update', kwargs={'pk': 1})
        data = {
            'name': '',
            'detail': 'This policy handles all aspects of dog care and behavior.'
        }
        response = self.client.post(url, data)
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form.errors['name'], ['This field is required.'])

class PolicyDeleteViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti',
            is_regional_manager=True)
        policy = Policy.objects.create(
            name='Dog Care',
            detail='This policy handles all aspects of dog care.')

    def test_policies_pk_delete_url_maps_to_policy_delete_name(self):
        url = '/policies/1/delete/'
        reversed_name = reverse('policy-delete', kwargs={'pk': 1})
        self.assertEqual(url, reversed_name)

    def test_reverse_policy_delete_name_resolves_to_policy_delete_view(self):
        view = resolve(reverse('policy-delete', kwargs={'pk': 1}))
        self.assertEqual(view.func.view_class, PolicyDelete)

    def test_reverse_policy_delete_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-delete', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'policies/confirm_delete.html')

    def test_reverse_policy_delete_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('policy-delete', kwargs={'pk': 1})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_policy_delete_name_success_status_code_if_logged_in_as_regional_manager(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-delete', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_policy_delete_name_not_found_status_code(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-delete', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_policy_delete_name_forbidden_status_code_if_logged_in_as_other_than_regional_manager(self):
        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = False
        user.save()

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-delete', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_reverse_policy_delete_name_redirects_to_current_page_after_logging_in_as_regional_manager(self):
        url = reverse('policy-delete', kwargs={'pk': 1})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url

        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = True
        user.save()
        
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)

    def test_reverse_policy_delete_name_form_csrf(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-delete', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_reverse_policy_delete_name_valid_post_data(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-delete', kwargs={'pk': 1})
        response = self.client.post(url, {})
        self.assertEqual(Policy.objects.all().count(), 0)

    def test_reverse_policy_delete_name_redirects_to_policy_list_name_after_valid_post(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('policy-delete', kwargs={'pk': 1})
        response = self.client.post(url, {})
        success_url = reverse('policy-list')
        self.assertRedirects(response, success_url)

class SectionCreateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti',
            is_regional_manager=True)
        policy = Policy.objects.create(
            name='Dog Care',
            detail='This policy handles all aspects of dog care.')
        section = Section.objects.create(
            policy=policy,
            name='Training',
            detail='Training your dog takes patience and a lot of repetition.')

    def test_policies_pk_sections_new_url_maps_to_section_create_name(self):
        url = '/policies/1/sections/new/'
        reversed_name = reverse('section-create', kwargs={'pk': 1})
        self.assertEqual(url, reversed_name)

    def test_reverse_section_create_not_found_status_code_if_policy_does_not_exist(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-create', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_section_create_name_resolves_to_section_create_view(self):
        view = resolve(reverse('section-create', kwargs={'pk': 1}))
        self.assertEqual(view.func.view_class, SectionCreate)

    def test_reverse_section_create_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-create', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'policies/section_form.html')

    def test_reverse_section_create_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('section-create', kwargs={'pk': 1})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))
        
    def test_reverse_section_create_name_redirects_to_current_page_after_logging_in_as_regional_manager(self):
        url = reverse('section-create', kwargs={'pk': 1})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url

        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)
        
    def test_reverse_section_create_name_success_status_code_if_logged_in_as_regional_manager(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-create', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_section_create_name_forbidden_status_code_if_logged_in_as_other_than_regional_manager(self):
        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = False
        user.save()

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-create', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_reverse_section_create_name_form_csrf(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-create', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_reverse_section_create_name_valid_post_data(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-create', kwargs={'pk': 1})
        data = {
            'name': 'Feeding',
            'detail': 'This sections discusses how and what to feed your dog.'
        }
        response = self.client.post(url, data)
        section = Section.objects.get(pk=2)
        self.assertEqual(section.policy.name, 'Dog Care')
        self.assertEqual(section.name, 'Feeding')
        self.assertEqual(section.detail, 'This sections discusses how and what to feed your dog.')
        self.assertEqual(Policy.objects.all().count(), 1)
        self.assertEqual(Section.objects.all().count(), 2)

    def test_reverse_section_create_name_redirects_to_policy_list_name_after_valid_post(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-create', kwargs={'pk': 1})
        data = {
            'name': 'Feeding',
            'detail': 'This sections discusses how and what to feed your dog.'
        }
        response = self.client.post(url, data)
        success_url = reverse('policy-list')
        self.assertRedirects(response, success_url)

    def test_reverse_section_create_name_invalid_post_data_empty_fields_returns_with_name_and_detail_fields_required_error(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-create', kwargs={'pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form.errors['name'], ['This field is required.'])
        self.assertEqual(form.errors['detail'], ['This field is required.'])
        
    def test_reverse_section_create_name_invalid_policy_pk_in_url_returns_with_not_found_status_code(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = '/policies/99/sections/new/'
        data = {
            'name': 'Feeding',
            'detail': 'This sections discusses how and what to feed your dog.'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)

class SectionUpdateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti',
            is_regional_manager=True)
        policy = Policy.objects.create(
            name='Dog Care',
            detail='This policy handles all aspects of dog care.')
        section = Section.objects.create(
            policy=policy,
            name='Training',
            detail='Training your dog takes patience and a lot of repetition.')

    def test_policies_pk_sections_pk_update_url_maps_to_section_update_name(self):
        url = '/policies/1/sections/1/update/'
        reversed_name = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        self.assertEqual(url, reversed_name)

    def test_reverse_section_update_not_found_status_code_if_policy_does_not_exist(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-update', kwargs={'policy_pk': 99, 'section_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_section_update_not_found_status_code_if_section_does_not_exist(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk':99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_section_update_name_resolves_to_section_update_view(self):
        view = resolve(reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1}))
        self.assertEqual(view.func.view_class, SectionUpdate)

    def test_reverse_section_update_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'policies/section_form.html')

    def test_reverse_section_update_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_section_update_name_redirects_to_current_page_after_logging_in_as_regional_manager(self):
        url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)

    def test_reverse_section_update_name_success_status_code_if_logged_in_as_regional_manager(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_sections_update_name_forbidden_status_code_if_logged_in_as_other_than_regional_manager(self):
        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = False
        user.save()

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_reverse_section_update_name_form_csrf(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_reverse_section_update_name_valid_post_data(self):
        section = Section.objects.get(pk=1)
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        data = {
            'name': 'Basic Training',
            'detail': section.detail,
        }
        response = self.client.post(url, data)
        section.refresh_from_db()
        self.assertEqual(section.policy.name, 'Dog Care')
        self.assertEqual(section.name, 'Basic Training')
        self.assertEqual(section.detail, 'Training your dog takes patience and a lot of repetition.')
        self.assertEqual(Policy.objects.all().count(), 1)
        self.assertEqual(Section.objects.all().count(), 1)

    def test_reverse_section_update_name_redirects_to_policy_list_name_after_valid_post(self):
        section = Section.objects.get(pk=1)
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        data = {
            'name': 'Basic Training',
            'detail': section.detail,
        }
        response = self.client.post(url, data)
        success_url = reverse('policy-list')
        self.assertRedirects(response, success_url)

    def test_reverse_section_update_name_invalid_post_data_empty_fields_returns_with_name_and_detail_fields_required_error(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form.errors['name'], ['This field is required.'])
        self.assertEqual(form.errors['detail'], ['This field is required.'])

class SectionDeleteViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti',
            is_regional_manager=True)
        policy = Policy.objects.create(
            name='Dog Care',
            detail='This policy handles all aspects of dog care.')
        section = Section.objects.create(
            policy=policy,
            name='Training',
            detail='Training your dog takes patience and a lot of repetition.')

    def test_policies_pk_sections_pk_delete_url_maps_to_section_delete_name(self):
        url = '/policies/1/sections/1/delete/'
        reversed_name = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 1})
        self.assertEqual(url, reversed_name)

    def test_reverse_section_delete_name_not_found_status_code_if_policy_does_not_exist(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-delete', kwargs={'policy_pk': 99, 'section_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_section_delete_name_not_found_status_code_if_section_does_not_exist(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk':99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_section_delete_name_resolves_to_section_delete_view(self):
        view = resolve(reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 1}))
        self.assertEqual(view.func.view_class, SectionDelete)

    def test_reverse_section_delete_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'policies/confirm_delete.html')

    def test_reverse_section_delete_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 1})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_section_delete_name_redirects_to_current_page_after_logging_in_as_regional_manager(self):
        url = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 1})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)

    def test_reverse_section_delete_name_success_status_code_if_logged_in_as_regional_manager(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_sections_update_name_forbidden_status_code_if_logged_in_as_other_than_regional_manager(self):
        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = False
        user.save()

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_reverse_section_delete_name_form_csrf(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_reverse_section_delete_name_valid_post_data(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.post(url, {})
        self.assertEqual(Policy.objects.all().count(), 1)
        self.assertEqual(Section.objects.all().count(), 0)

    def test_reverse_section_delete_name_redirects_to_policy_list_name_after_valid_post(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.post(url, {})
        success_url = reverse('policy-list')
        self.assertRedirects(response, success_url)

class SectionMoveViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti',
            is_regional_manager=True)
        policy = Policy.objects.create(
            name='Dog Care',
            detail='This policy handles all aspects of dog care.')
        section = Section.objects.create(
            policy=policy,
            name='Training',
            detail='Training your dog takes patience and a lot of repetition.')

    def test_policies_pk_sections_pk_move_url_maps_to_section_move_name(self):
        url = '/policies/1/sections/1/move/'
        reversed_name = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        self.assertEqual(url, reversed_name)

    def test_reverse_section_move_name_not_found_status_code_if_policy_does_not_exist(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-move', kwargs={'policy_pk': 99, 'section_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_section_move_name_not_found_status_code_if_section_does_not_exist(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk':99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reverse_section_move_name_resolves_to_section_move_view(self):
        view = resolve(reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1}))
        self.assertEqual(view.func.view_class, SectionMove)

    def test_reverse_section_move_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'policies/section_form.html')

    def test_reverse_section_move_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_section_move_name_redirects_to_current_page_after_logging_in_as_regional_manager(self):
        url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)

    def test_reverse_section_move_name_success_status_code_if_logged_in_as_regional_manager(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_sections_update_name_forbidden_status_code_if_logged_in_as_other_than_regional_manager(self):
        user = CustomUser.objects.get(username='carol')
        user.is_regional_manager = False
        user.save()

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_reverse_section_move_name_form_csrf(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_reverse_section_move_name_valid_post_data(self):
        policy = Policy.objects.create(name='Dog Behavior')
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        data =  {
            'policy': '2',
        }
        response = self.client.post(url, data)
        self.assertEqual(Policy.objects.all().count(), 2)
        self.assertEqual(Section.objects.all().count(), 1)

    def test_reverse_section_move_name_redirects_to_policy_list_name_after_valid_post(self):
        policy = Policy.objects.create(name='Dog Behavior')
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        data =  {
            'policy': '2',
        }
        response = self.client.post(url, data)
        success_url = reverse('policy-list')
        self.assertRedirects(response, success_url)

    def test_reverse_section_move_name_invalid_post_data_empty_fields_returns_with_policy_required_error(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form.errors['policy'], ['This field is required.'])