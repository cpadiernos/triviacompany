import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models

class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name

private_storage = OverwriteStorage(
    location=settings.PRIVATE_STORAGE_ROOT,
    base_url=settings.PRIVATE_STORAGE_URL)

class Game(models.Model):
    date = models.DateField(null=True, blank=True)
    question_set = models.FileField(
        upload_to='question_sets/', blank=True, storage=private_storage)
    worksheet = models.FileField(
        upload_to='worksheets/', blank=True, storage=private_storage)
    notes = models.TextField(blank=True)

    # class Meta:
        # db_table = 'game'

    def __str__(self):
        return '{0} - {1}'.format(self.date, self.question_set)

    @property
    def question_set_filename(self):
        return os.path.basename(self.question_set.name)

    @property
    def worksheet_filename(self):
        return os.path.basename(self.worksheet.name)