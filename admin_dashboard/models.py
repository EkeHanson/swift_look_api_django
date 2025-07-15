from django.db import models
from users.models import CustomUser

class Device(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='admin_dashboard_devices')
    device_name = models.CharField(max_length=255)
    imei_number = models.CharField(max_length=20, unique=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    last_location = models.JSONField()  # Store location data as JSON
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('lost', 'Lost'), ('recovered', 'Recovered')])

    def __str__(self):
        return f"{self.device_name} ({self.imei_number})"

class TrackingLog(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='tracking_logs')
    location = models.JSONField() 
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20, choices=[('location_update', 'Location Update'), ('remote_lock', 'Remote Lock'), ('data_wipe', 'Data Wipe')])

    def __str__(self):
        return f"{self.device.device_name} - {self.timestamp}"

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.device.device_name} - {self.sent_at}"

# class UserAccessLog(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='access_logs')
#     action = models.CharField(max_length=255)  # e.g., 'Login', 'Profile Update'
#     ip_address = models.GenericIPAddressField(null=True, blank=True)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.email} - {self.action} at {self.timestamp}"
