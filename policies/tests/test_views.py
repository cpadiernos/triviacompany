from django.test import TestCase
from django.urls import reverse, resolve
from policies.models import Policy, Section
from policies.views import PolicyListView, PolicyCreate, PolicyUpdate, PolicyDelete
from policies.views import SectionCreate, SectionUpdate, SectionDelete, SectionMove

class PolicyViewTests(TestCase):
    def setUp(self):
        Policy.objects.create(name='Dog Care', detail='This policy handles all aspects of dog care.')
    
    def test_policies_view_success_status_code(self):
        url = reverse('policy-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_policies_url_resolves_policy_list_view(self):
        view = resolve('/policies/')
        self.assertEqual(view.func.view_class, PolicyListView)
        
    def test_policies_new_view_success_status_code(self):
        url = reverse('policy-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_policies_new_url_resolves_policy_create(self):
        view = resolve('/policies/new/')
        self.assertEqual(view.func.view_class, PolicyCreate)
        
    def test_policies_update_view_success_status_code(self):
        url = reverse('policy-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_policies_update_view_not_found_status_code(self):
        url = reverse('policy-update', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_policies_update_url_resolves_policy_update(self):
        view = resolve('/policies/1/update/')
        self.assertEqual(view.func.view_class, PolicyUpdate)
    
    def test_policies_delete_view_success_status_code(self):
        url = reverse('policy-delete', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_policies_delete_view_not_found_status_code(self):
        url = reverse('policy-delete', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_policies_delete_url_resolves_policy_delete(self):
        view = resolve('/policies/1/delete/')
        self.assertEqual(view.func.view_class, PolicyDelete)
        
    def test_policies_view_contains_link_to_policy_update(self):
        policies_url = reverse('policy-list')
        policy_update_url = reverse('policy-update', kwargs={'pk': 1})
        response = self.client.get(policies_url)
        self.assertContains(response, 'href="{0}"'.format(policy_update_url))
        
    def test_policies_view_contains_link_to_policy_delete(self):
        policies_url = reverse('policy-list')
        policy_delete_url = reverse('policy-delete', kwargs={'pk': 1})
        response = self.client.get(policies_url)
        self.assertContains(response, 'href="{0}"'.format(policy_delete_url))
        
    def test_policies_view_contains_link_to_section_create(self):
        policies_url = reverse('policy-list')
        section_create_url = reverse('section-create', kwargs={'pk': 1})
        response = self.client.get(policies_url)
        self.assertContains(response, 'href="{0}"'.format(section_create_url))
        
    def test_policies_new_form_csrf(self):
        url = reverse('policy-create')
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')
        
    def test_policies_new_valid_post_data(self):
        url = reverse('policy-create')
        data = {
            'name': 'Cat Care',
            'detail': 'This policy handles all aspects of cat care.'
        }
        response = self.client.post(url, data)
        self.assertEqual(Policy.objects.all().count(), 2)
        
    def test_policies_new_invalid_post_data(self):
        url = reverse('policy-create')
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.errors)
        
    def test_policies_new_invalid_post_data_empty_fields(self):
        url = reverse('policy-create')
        data = {
            'name': '',
            'detail': ''
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Policy.objects.all().count(), 1)
        
    def test_policies_update_form_csrf(self):
        url = reverse('policy-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')
        
    def test_policies_update_valid_post_data(self):
        url = reverse('policy-update', kwargs={'pk': 1})
        data = {
            'name': 'Bear Care',
            'detail': 'This policy discusses everything about caring for your bear.'
        }
        response = self.client.post(url, data)
        updated_policy = Policy.objects.get(pk=1)
        updated_policy_name = updated_policy.name
        self.assertEqual(updated_policy_name, 'Bear Care')
        self.assertEqual(Policy.objects.all().count(), 1)
        
    def test_policies_update_invalid_post_data(self):
        url = reverse('policy-update', kwargs={'pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.errors)
        
    def test_policies_update_invalid_post_data_empty_fields(self):
        url = reverse('policy-update', kwargs={'pk': 1})
        data = {
            'name': '',
            'detail': ''
        }
        response = self.client.post(url, data)
        policy = Policy.objects.get(pk=1)
        policy_name = policy.name
        self.assertEqual(policy_name, 'Dog Care')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Policy.objects.all().count(), 1)
        
    def test_policies_delete_form_csrf(self):
        url = reverse('policy-delete', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_policies_delete_valid_post_data(self):
        url = reverse('policy-delete', kwargs={'pk': 1})
        response = self.client.post(url, {})
        self.assertEqual(Policy.objects.all().count(), 0)
        self.assertEqual(Section.objects.all().count(), 0)

class SectionViewTests(TestCase):
    def setUp(self):
        policy = Policy.objects.create(name='Dog Care', detail='This policy handles all aspects of dog care.')
        Section.objects.create(policy=policy, name='Training', detail='Training your dog takes patience and a lot of repetition.')
        Policy.objects.create(name='Dog Behavior', detail='This policy discusses working with general dog behavior.')
  
    def test_sections_new_view_success_status_code(self):
        url = reverse('section-create', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_sections_new_view_not_found_status_code(self):
        url = reverse('section-create', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_sections_new_url_resolves_section_create(self):
        view = resolve('/policies/1/sections/new/')
        self.assertEqual(view.func.view_class, SectionCreate)
        
    def test_sections_update_view_success_status_code(self):
        url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_sections_update_view_not_found_status_code_policy_does_not_exist(self):
        url = reverse('section-update', kwargs={'policy_pk': 99, 'section_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_sections_update_view_not_found_status_code_section_does_not_exist(self):
        url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_sections_update_url_resolves_section_update(self):
        view = resolve('/policies/1/sections/1/update/')
        self.assertEqual(view.func.view_class, SectionUpdate)
        
    def test_sections_delete_view_success_status_code(self):
        url = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_sections_delete_view_not_found_status_code_policy_does_not_exist(self):
        url = reverse('section-delete', kwargs={'policy_pk': 99, 'section_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_sections_delete_view_not_found_status_code_section_does_not_exist(self):
        url = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_sections_delete_url_resolves_section_delete(self):
        view = resolve('/policies/1/sections/1/delete/')
        self.assertEqual(view.func.view_class, SectionDelete)
    
    def test_sections_move_view_success_status_code(self):
        url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_sections_move_view_not_found_status_code_policy_does_not_exist(self):
        url = reverse('section-move', kwargs={'policy_pk': 99, 'section_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_sections_move_view_not_found_status_code_section_does_not_exist(self):
        url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_sections_move_url_resolves_section_move(self):
        view = resolve('/policies/1/sections/1/move/')
        self.assertEqual(view.func.view_class, SectionMove)
    
    def test_policies_view_with_sections_contains_link_to_section_update(self):
        policies_url = reverse('policy-list')
        section_update_url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(policies_url)
        self.assertContains(response, 'href="{0}"'.format(section_update_url))
   
    def test_policies_view_with_sections_contains_link_to_section_delete(self):
        policies_url = reverse('policy-list')
        section_delete_url = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(policies_url)
        self.assertContains(response, 'href="{0}"'.format(section_delete_url))
    
    def test_sections_new_form_csrf(self):
        url = reverse('section-create', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')
        
    def test_sections_new_valid_post_data(self):
        url = reverse('section-create', kwargs={'pk': 1})
        data = {
            'name': 'Walks',
            'detail': 'Younger dogs and older dogs should be taken out more frequently.'
        }
        response = self.client.post(url, data)
        self.assertEqual(Section.objects.all().count(), 2)
        
    def test_sections_new_invalid_post_data(self):
        url = reverse('section-create', kwargs={'pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.errors)
        
    def test_sections_new_invalid_post_data_empty_fields(self):
        url = reverse('section-create', kwargs={'pk': 1})
        data = {
            'name': '',
            'detail': ''
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Section.objects.all().count(), 1)
        
    def test_sections_update_form_csrf(self):
        url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')
        
    def test_sections_update_valid_post_data(self):
        url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        data = {
            'name': 'Walks',
            'detail': 'Younger dogs and older dogs should be taken out more frequently.'
        }
        response = self.client.post(url, data)
        updated_section = Section.objects.get(pk=1)
        updated_section_name = updated_section.name
        self.assertEqual(updated_section_name, 'Walks')
        self.assertEqual(Section.objects.all().count(), 1)
        
    def test_sections_update_invalid_post_data(self):
        url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.errors)
        
    def test_sections_update_invalid_post_data_empty_fields(self):
        url = reverse('section-update', kwargs={'policy_pk': 1, 'section_pk': 1})
        data = {
            'name': '',
            'detail': ''
        }
        response = self.client.post(url, data)
        section = Section.objects.get(pk=1)
        section_name = section.name
        self.assertEqual(section_name, 'Training')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Section.objects.all().count(), 1)
        
    def test_sections_delete_form_csrf(self):
        url = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_sections_delete_valid_post_data(self):
        url = reverse('section-delete', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.post(url, {})
        self.assertEqual(Section.objects.all().count(), 0)
        
    def test_sections_move_form_csrf(self):
        url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')
        
    def test_sections_move_valid_post_data(self):
        url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        data = {
            'policy': '2', 
        }
        response = self.client.post(url, data)
        updated_section = Section.objects.get(pk=1)
        updated_section_policy = updated_section.policy
        self.assertEqual(updated_section_policy, Policy.objects.get(pk=2))
        
    def test_sections_move_invalid_post_data(self):
        url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.errors)
        
    def test_sections_move_invalid_post_data_empty_fields(self):
        url = reverse('section-move', kwargs={'policy_pk': 1, 'section_pk': 1})
        data = {
            'policy': '',
        }
        response = self.client.post(url, data)
        section_policy = Section.objects.get(pk=1).policy
        self.assertEqual(section_policy, Policy.objects.get(pk=1))
        self.assertEqual(response.status_code, 200)