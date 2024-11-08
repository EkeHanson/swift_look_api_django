# users/serializers.py
from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    user_type = serializers.CharField(default='client')
    is_active = serializers.CharField(default='in_active')
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = "__all__"
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True, 
        min_length=8, 
        required=True,
        error_messages={
            'required': 'New password is required.',
            'min_length': 'Password must be at least 8 characters long.'
        }
    )

