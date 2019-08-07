# Generated by Django 2.2 on 2019-07-15 23:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('schedule', '0003_auto_20190618_1847'),
    ]

    operations = [
        migrations.CreateModel(
            name='PayStub',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pay_date', models.DateField(blank=True, null=True)),
                ('total_gross_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('total_reimbursement_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('paid', models.BooleanField(default=False, verbose_name='paid')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pay_stubs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['pay_date'],
            },
        ),
        migrations.CreateModel(
            name='SalaryPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week_start', models.DateField(blank=True, null=True)),
                ('week_end', models.DateField(blank=True, null=True)),
                ('gross_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('paid', models.BooleanField(default=False, verbose_name='paid')),
                ('pay_stub', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='salary_payments', to='accounting.PayStub')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='salary_payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['week_end'],
            },
        ),
        migrations.CreateModel(
            name='EventOccurrencePayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, choices=[('P', 'Payment'), ('C', 'Correction')], default='P', max_length=1)),
                ('submission_date', models.DateField(blank=True, null=True)),
                ('gross_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('paid', models.BooleanField(default=False, verbose_name='paid')),
                ('event_occurrence', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_occurrence_payments', to='schedule.EventOccurrence')),
                ('pay_stub', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_occurrence_payments', to='accounting.PayStub')),
            ],
            options={
                'ordering': ['submission_date', 'pay_stub'],
            },
        ),
    ]
