# devices/serializers.py
from rest_framework import serializers
from .models import Device
from users.models import CustomUser


class UpdateLocationSerializer(serializers.Serializer):
    imei = serializers.CharField(max_length=15)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)

    
class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["phone", "first_name", "last_name", "user_type",  "is_active", "email"]

 

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"

# Serializer that includes only user fields in GET requests
class DeviceSummarySerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)  # This includes the user's fields from UserSummarySerializer

    class Meta:
        model = Device
        fields = fields = "__all__"