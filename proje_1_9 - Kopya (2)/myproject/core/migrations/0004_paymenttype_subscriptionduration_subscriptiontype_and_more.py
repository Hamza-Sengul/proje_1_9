# Generated by Django 5.1.4 on 2025-03-13 03:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_expensecategorylog'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionDuration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150, unique=True)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('identification', models.CharField(blank=True, max_length=100, null=True, verbose_name='TC/Vergi No')),
                ('tax_office', models.CharField(blank=True, max_length=150, null=True, verbose_name='Vergi Dairesi')),
                ('address', models.TextField()),
                ('subscription_start_date', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('agreement_status', models.CharField(choices=[('olumlu', 'Olumlu'), ('olumsuz', 'Olumsuz')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('rep', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Temsilci')),
                ('payment_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.paymenttype')),
                ('subscription_duration', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.subscriptionduration')),
                ('subscription_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.subscriptiontype')),
            ],
        ),
    ]
