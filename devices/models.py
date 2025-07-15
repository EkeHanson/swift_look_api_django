from django.db import models
from users.models import CustomUser
from django.utils.timezone import now
import uuid
from django_cryptography.fields import encrypt

class Device(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, to_field='unique_user_id', related_name='device_links')
    unique_device_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    imei1 = encrypt(models.CharField(max_length=15, unique=True, null=True, blank=True))
    imei2 = encrypt(models.CharField(max_length=15, unique=True, null=True, blank=True))
    image1 = models.ImageField(upload_to='device_images', blank=True, null=True)
    image2 = models.ImageField(upload_to='device_images', blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    is_tracked = models.BooleanField(default=False)
    
    # Location fields
    street = models.CharField(max_length=255, null=True, blank=True)
    building_number = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    nearby_landmark = models.CharField(max_length=255, null=True, blank=True)
    location_accuracy = models.CharField(max_length=50, null=True, blank=True)
    altitude = models.CharField(max_length=50, null=True, blank=True)
    
    # Device status
    battery_level = models.IntegerField(null=True, blank=True)
    speed = models.CharField(max_length=50, null=True, blank=True)
    direction = models.CharField(max_length=50, null=True, blank=True)
    last_online = models.DateTimeField(null=True, blank=True)
    connected_wifi = models.CharField(max_length=100, null=True, blank=True)
    device_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('lost', 'Lost'), ('recovered', 'Recovered')], default='active')

    class Meta:
        indexes = [
            models.Index(fields=['unique_device_id']),
            models.Index(fields=['imei1']),
            models.Index(fields=['imei2']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return self.name

class TrackableLink(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='trackable_links')
    link = models.URLField(max_length=500)
    is_clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    browser = models.CharField(max_length=50, blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    os_info = models.CharField(max_length=100, blank=True)
    screen_resolution = models.CharField(max_length=50, blank=True)
    referrer_url = models.URLField(max_length=500, blank=True)
    geolocation = models.JSONField(null=True, blank=True)
    campaign_params = models.JSONField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['device', 'is_clicked']),
        ]

    def __str__(self):
        return f"Trackable Link for {self.device.name}"