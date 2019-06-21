# Generated by Django 2.2 on 2019-06-18 22:47

import accounts.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phone_field.models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0002_auto_20190506_1401'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_host',
            field=models.BooleanField(default=False, verbose_name='host'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_regional_manager',
            field=models.BooleanField(default=False, verbose_name='RM'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_venue_manager',
            field=models.BooleanField(default=False, verbose_name='VM'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='mailing_additional_address',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='customuser',
            name='mailing_address',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='customuser',
            name='mailing_city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='locations.City'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='mailing_state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='locations.State'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='mailing_zip',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='locations.Zip'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='mobile_number',
            field=phone_field.models.PhoneField(blank=True, max_length=12),
        ),
        migrations.AddField(
            model_name='customuser',
            name='profile_image',
            field=models.ImageField(blank=True, storage=accounts.models.OverwriteStorage(), upload_to='profile_images'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='secondary_email',
            field=models.EmailField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='customuser',
            name='work_number',
            field=phone_field.models.PhoneField(blank=True, max_length=12),
        ),
        migrations.CreateModel(
            name='VenueManagerProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('best_reached_by', models.CharField(blank=True, choices=[('Cell', 'Cellphone'), ('Venue', 'Venue phone'), ('Email', 'Email')], max_length=5)),
                ('user', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='venue_manager_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RegionalManagerProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekly_pay', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='regional_manage_profiles', to='locations.Region')),
                ('user', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='regional_manager_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HostProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True)),
                ('has_event', models.BooleanField(default=True, verbose_name='has event')),
                ('residential_address', models.CharField(blank=True, max_length=100)),
                ('base_rate', models.DecimalField(blank=True, decimal_places=2, default=50, max_digits=5, null=True)),
                ('base_teams', models.DecimalField(blank=True, decimal_places=2, default=5, max_digits=5, null=True)),
                ('incremental_rate', models.DecimalField(blank=True, decimal_places=2, default=2, max_digits=5, null=True)),
                ('incremental_teams', models.DecimalField(blank=True, decimal_places=2, default=1, max_digits=5, null=True)),
                ('residential_city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='host_profiles', to='locations.City')),
                ('user', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='host_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]