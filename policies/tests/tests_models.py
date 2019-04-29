from django.test import TestCase
from policies.models import Policy, Section

class PolicyModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Policy.objects.create(name='Cat Playtime', detail='Everything you need to know about playing with cats.')
        
    def test_name_label(self):
        policy = Policy.objects.get(id=1)
        field_label = policy._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')
        
    def test_name_max_length(self):
        policy = Policy.objects.get(id=1)
        max_length = policy._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)
        
    def test_verbose_name_plural(self):
        plural_name = Policy._meta.verbose_name_plural
        self.assertEqual(plural_name, 'policies') 
        
    def test_detail_label(self):
        policy = Policy.objects.get(id=1)
        field_label = policy._meta.get_field('detail').verbose_name
        self.assertEqual(field_label, 'detail')
        
    def test_string_representation(self):
        policy = Policy.objects.get(id=1)
        self.assertEqual(str(policy), policy.name)    
        
class SectionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        policy = Policy.objects.create(name='Cat Playtime', detail='Everything you need to know about playing with cats.')
        Section.objects.create(policy=policy, name='Laser Toy', detail='When playing with a laser toy, make sure the movements of the laser mimic the movements of a mouse.')
    
    def test_policy_label(self):
        section = Section.objects.get(id=1)
        field_label = section._meta.get_field('policy').verbose_name
        self.assertEqual(field_label, 'policy')

    def test_policy_related_name(self):
        section = Section.objects.get(id=1)
        related_name = section.policy._meta.get_field('sections').related_name
        self.assertEqual(related_name, 'sections')
        
    def test_policy_delete_cascade(self):
        policy = Policy.objects.get(id=1)
        policy.delete()
        count = Section.objects.all().count()
        self.assertEqual(count, 0)
        
    def test_name_label(self):
        section = Section.objects.get(id=1)
        field_label = section._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')
        
    def test_name_max_length(self):
        section = Section.objects.get(id=1)
        max_length = section._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)
        
    def test_detail_label(self):
        section = Section.objects.get(id=1)
        field_label = section._meta.get_field('detail').verbose_name
        self.assertEqual(field_label, 'detail')
        
    def test_string_representation(self):
        section = Section.objects.get(id=1)
        self.assertEqual(str(section), section.name)