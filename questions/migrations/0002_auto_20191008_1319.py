# Generated by Django 2.2 on 2019-10-08 17:19

from django.db import migrations, models
import questions.models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='question_set',
            field=models.FileField(blank=True, storage=questions.models.OverwriteStorage(), upload_to='question_sets/'),
        ),
        migrations.AlterField(
            model_name='game',
            name='worksheet',
            field=models.FileField(blank=True, storage=questions.models.OverwriteStorage(), upload_to='worksheets/'),
        ),
    ]
