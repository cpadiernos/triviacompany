import os
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from questions.models import Game

TEMP_FILE_LOCATION = 'temp_game_files'

class GameModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Game.question_set.field.storage.location = TEMP_FILE_LOCATION
        test_question_set = SimpleUploadedFile(
            'test_question_set.txt', b'test question set text')
        test_worksheet = SimpleUploadedFile(
            'test_worksheet.txt', b'test worksheet text')
        game = Game.objects.create(
            question_set=test_question_set,
            worksheet=test_worksheet)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_FILE_LOCATION)
        super().tearDownClass()

    def test_date_label(self):
        game = Game.objects.get(pk=1)
        field_label = game._meta.get_field('date').verbose_name
        self.assertEqual(field_label, 'date')

    def test_question_set_label(self):
        game = Game.objects.get(pk=1)
        field_label = game._meta.get_field('question_set').verbose_name
        self.assertEqual(field_label, 'question set')

    def test_question_set_uploads_to_question_sets_filename(self):
        game = Game.objects.get(pk=1)
        filename = 'test_question_set.txt'
        folder = 'question_sets'
        self.assertEqual(
            game.question_set.name,
            '{0}/{1}'.format(folder, filename))

    def test_question_set_with_same_name_deletes_file(self):
        test_question_set = SimpleUploadedFile('test_question_set.txt', b'test question set text')
        game = Game.objects.get(pk=1)
        game.question_set = test_question_set
        game.save()
        
        total = 0
        for root, dirs, files in os.walk(TEMP_FILE_LOCATION):
            if 'test_question_set.txt' in files:
                total += len(files)
        self.assertEqual(total, 1)

    def test_worksheet_label(self):
        game = Game.objects.get(pk=1)
        field_label = game._meta.get_field('worksheet').verbose_name
        self.assertEqual(field_label, 'worksheet')

    def test_worksheet_uploads_to_worksheets_filename(self):
        game = Game.objects.get(pk=1)
        filename = 'test_worksheet.txt'
        folder = 'worksheets'
        self.assertEqual(
            game.worksheet.name,
            '{0}/{1}'.format(folder, filename))

    def test_worksheet_with_same_name_deletes_file(self):
        test_worksheet = SimpleUploadedFile('test_worksheet.txt', b'test worksheet text')
        game = Game.objects.get(pk=1)
        game.worksheet = test_worksheet
        game.save()

        total = 0
        for root, dirs, files in os.walk(TEMP_FILE_LOCATION):
            if 'test_worksheet.txt' in files:
                total += len(files)
        self.assertEqual(total, 1)

    def test_notes_label(self):
        game = Game.objects.get(pk=1)
        field_label = game._meta.get_field('notes').verbose_name
        self.assertEqual(field_label, 'notes')

    def test_game_str_returns_date_question_set(self):
        game = Game.objects.get(pk=1)
        self.assertEqual(str(game), '{0} - {1}'.format(game.date, game.question_set))

    def test_question_set_filename_returns_only_filename(self):
        game = Game.objects.get(pk=1)
        self.assertEqual(game.question_set_filename, 'test_question_set.txt')

    def test_worksheet_filename_returns_only_filename(self):
        game = Game.objects.get(pk=1)
        self.assertEqual(game.worksheet_filename, 'test_worksheet.txt')