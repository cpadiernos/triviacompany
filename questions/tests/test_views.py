import datetime
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse, resolve

from accounts.models import CustomUser
from questions.models import Game
from questions.views import GameListView, login_required_private_file

TEMP_FILE_LOCATION = 'temp_game_files'

class GameListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        Game.question_set.field.storage.location = TEMP_FILE_LOCATION

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_FILE_LOCATION)
        super().tearDownClass()

    def test_game_supplies_url_maps_to_game_list_name(self):
        url = '/game-supplies/'
        reversed_name = reverse('game-list')
        self.assertEqual(url, reversed_name)
        
    def test_game_list_name_resolves_to_game_list_view_view(self):
        view = resolve(reverse('game-list'))
        self.assertEqual(view.func.view_class, GameListView)

    def test_reverse_game_list_name_uses_correct_template(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('game-list')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'questions/game_list.html')

    def test_reverse_game_list_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        url = reverse('game-list')
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_game_list_name_success_status_code_if_logged_in(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('game-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reverse_game_list_name_redirects_to_current_page_after_logging_in(self):
        url = reverse('game-list')
        response_before_login = self.client.get(url)
        login_url = response_before_login.url
        response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'})
        self.assertRedirects(response_after_login, url)

    def test_reverse_game_list_name_includes_all_games_today_and_in_future(self):
        day_before_today = datetime.date.today() - datetime.timedelta(days=1)
        today = datetime.date.today()
        day_after_today = datetime.date.today() + datetime.timedelta(days=1)

        game_past = Game.objects.create(date=day_before_today)
        game_current = Game.objects.create(date=today)
        game_future = Game.objects.create(date=day_after_today)

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('game-list')
        response = self.client.get(url)
        # leading spaces in case test is done at beginning of the month (for months after months with 31 days)
        # i.e. " 1, 2019" should pass, but " 31,2019" should not.
        self.assertNotContains(response, f' {day_before_today.day}, {day_before_today.year}')
        self.assertContains(response, f' {today.day}, {today.year}')
        self.assertContains(response, f' {day_after_today.day}, {day_after_today.year}')

    def test_reverse_game_list_name_contains_link_to_files(self):
        today = datetime.date.today()
        test_question_set = SimpleUploadedFile(
            'test_question_set.txt', b'test question set text')
        test_worksheet = SimpleUploadedFile(
            'test_worksheet.txt', b'test worksheet text')
        game = Game.objects.create(
            date=today,
            question_set=test_question_set,
            worksheet=test_worksheet)

        login = self.client.login(username='carol', password='Ilovespaghetti')
        url = reverse('game-list')
        question_set_url = reverse('login-required-private-file', kwargs={'path': game.question_set.name})
        worksheet_url = reverse('login-required-private-file', kwargs={'path': game.worksheet.name})
        response = self.client.get(url)
        self.assertContains(response, 'href="{0}"'.format(question_set_url))
        self.assertContains(response, 'href="{0}"'.format(worksheet_url))

class LoginRequiredPrivateFileView(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            username='carol', password='Ilovespaghetti')
        Game.question_set.field.storage.location = TEMP_FILE_LOCATION
        today = datetime.date.today()
        test_question_set = SimpleUploadedFile(
            'test_question_set.txt', b'test question set text')
        test_worksheet = SimpleUploadedFile(
            'test_worksheet.txt', b'test worksheet text')
        game = Game.objects.create(
            date=today,
            question_set=test_question_set,
            worksheet=test_worksheet)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_FILE_LOCATION)
        super().tearDownClass()

    def test_private_storage_path_url_maps_to_login_required_private_file_name(self):
        game = Game.objects.get(pk=1)
        url = '/{0}/{1}'.format(settings.PRIVATE_STORAGE_URL[1:-1], game.question_set.name)
        reversed_name = reverse('login-required-private-file', kwargs={'path': game.question_set.name})
        self.assertEqual(url, reversed_name)

    def test_reverse_login_required_private_file_name_resolves_to_login_required_private_file_view(self):
        game = Game.objects.get(pk=1)
        view = resolve(reverse('login-required-private-file', kwargs={'path': game.question_set.name}))
        self.assertEqual(view.func, login_required_private_file)

    def test_reverse_login_required_private_file_name_redirects_to_accounts_login_page_if_not_logged_in(self):
        game = Game.objects.get(pk=1)
        url = reverse('login-required-private-file', kwargs={'path': game.question_set.name})
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, url))

    def test_reverse_login_required_private_file_name_success_status_code_if_logged_in(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        game = Game.objects.get(pk=1)
        with self.settings(PRIVATE_STORAGE_ROOT=TEMP_FILE_LOCATION):
            url = reverse('login-required-private-file', kwargs={'path': game.question_set.name})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            response.close()

    def test_reverse_login_required_private_file_name_redirects_to_current_page_after_logging_in(self):
        game = Game.objects.get(pk=1)
        with self.settings(PRIVATE_STORAGE_ROOT=TEMP_FILE_LOCATION):
            url = reverse('login-required-private-file', kwargs={'path': game.question_set.name})
            response_before_login = self.client.get(url)
            login_url = response_before_login.url
            response_after_login = self.client.post(login_url, {'username': 'carol', 'password': 'Ilovespaghetti'}, follow=True)
            self.assertRedirects(response_after_login, url)
            response_after_login.close()

    def test_reverse_login_required_private_file_name_not_found_status_code_if_logged_in_and_file_does_not_exist(self):
        login = self.client.login(username='carol', password='Ilovespaghetti')
        game = Game.objects.get(pk=1)
        with self.settings(PRIVATE_STORAGE_ROOT=TEMP_FILE_LOCATION):
            url = reverse('login-required-private-file', kwargs={'path': 'nonexistent_file.txt'})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)