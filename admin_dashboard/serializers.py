from rest_framework import serializers
from users.models import CustomUser
from rest_framework import serializers
from devices.models import Device


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email','phone','first_name']


class DeviceSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()  # Use the nested serializer for the user field
    class Meta:
        model = Device
        fields = "__all__"


class CustomDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    # is_active = serializers.BooleanField()
    devices = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = "__all__"

    def get_devices(self, obj):
        return DeviceSerializer(obj.device_set.all(), many=True).data      

# from rest_framework import serializers
# from tracking.models import TrackingHistory

# class TrackingHistorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TrackingHistory
#         fields = ['id', 'device', 'timestamp', 'location']


# from rest_framework import serializers
# from notifications.models import Notification

# class NotificationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Notification
#         fields = ['id', 'user', 'device', 'message', 'timestamp']
