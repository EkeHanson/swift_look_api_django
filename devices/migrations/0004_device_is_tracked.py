# Generated by Django 5.0.2 on 2024-11-08 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0003_device_ip_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='is_tracked',
            field=models.BooleanField(default=False),
        ),
    ]
