from django.contrib import admin
from .models import Device, TrackingLog, Notification

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'imei_number', 'status', 'registered_at')
    search_fields = ('device_name', 'imei_number')

@admin.register(TrackingLog)
class TrackingLogAdmin(admin.ModelAdmin):
    list_display = ('device', 'location', 'timestamp', 'action')
    search_fields = ('device__device_name', 'action')
    list_filter = ('action', 'timestamp')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'device', 'message', 'sent_at')
    search_fields = ('user__username', 'device__device_name')
    list_filter = ('sent_at',)
