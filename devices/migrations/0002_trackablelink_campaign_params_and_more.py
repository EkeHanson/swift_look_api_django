# Generated by Django 5.0.2 on 2024-12-30 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trackablelink',
            name='campaign_params',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='trackablelink',
            name='geolocation',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='trackablelink',
            name='os_info',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='trackablelink',
            name='referrer_url',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='trackablelink',
            name='screen_resolution',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]