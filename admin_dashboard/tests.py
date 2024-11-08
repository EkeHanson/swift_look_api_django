from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Device, TrackingLog, Notification
from django.contrib.auth.models import User

class AdminDashboardTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(username='admin', password='password')
        self.client.force_authenticate(user=self.admin_user)
        self.device = Device.objects.create(device_name='Test Device', imei_number='123456789012345', status='active')
        self.tracking_log = TrackingLog.objects.create(device=self.device, location={'lat': 10.0, 'long': 10.0}, action='location_update')
        self.notification = Notification.objects.create(user=self.admin_user, device=self.device, message='Test Notification')

    def test_device_list(self):
        response = self.client.get('/admin_dashboard/devices/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tracking_log_list(self):
        response = self.client.get('/admin_dashboard/tracking-logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notification_list(self):
        response = self.client.get('/admin_dashboard/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
