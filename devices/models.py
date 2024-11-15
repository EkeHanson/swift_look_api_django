from django.db import models
from users.models import CustomUser

class Device(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    image1 = models.ImageField(upload_to='device_images', blank=True, null=True)
    image2 = models.ImageField(upload_to='device_images', blank=True, null=True)

    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True, unique=True)
    
    imei1 = models.CharField(max_length=15, unique=True, null=True, blank=True)
    imei2 = models.CharField(max_length=15, unique=True, null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    
    # New field to show if the device is being tracked successfully
    is_tracked = models.BooleanField(default=False)

    # Location-based fields
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

    # Device-related fields
    battery_level = models.IntegerField(null=True, blank=True)
    speed = models.CharField(max_length=50, null=True, blank=True)
    direction = models.CharField(max_length=50, null=True, blank=True)

    # Connection and device details
    last_online = models.DateTimeField(null=True, blank=True)
    connected_wifi = models.CharField(max_length=100, null=True, blank=True)
    device_id = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name
