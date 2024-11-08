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

    def __str__(self):
        return self.name
