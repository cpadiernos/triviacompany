# Generated by Django 2.2 on 2019-06-28 20:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20190620_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regionalmanagerprofile',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='regional_manager_profiles', to='locations.Region'),
        ),
    ]