# Generated by Django 5.0.2 on 2024-12-30 08:01

import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('phone', models.CharField(max_length=15)),
                ('unique_user_id', models.CharField(default=uuid.uuid4, max_length=50, unique=True)),
                ('first_name', models.CharField(max_length=225)),
                ('last_name', models.CharField(max_length=225)),
                ('user_type', models.CharField(choices=[('admin', 'Admin'), ('user', 'User')], max_length=10)),
                ('is_active', models.CharField(choices=[('active', 'Active'), ('in_active', 'In_active')], max_length=10)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('username', models.CharField(blank=True, max_length=80, null=True)),
                ('email', models.EmailField(max_length=80, unique=True)),
                ('last_login_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('first_login_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('tracked_devices_count', models.IntegerField(default=0)),
                ('registered_devices_count', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
