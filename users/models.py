from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, phone, request=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        user_type = extra_fields.pop('user_type', 'student')
        email = self.normalize_email(email)
        user = self.model(
            email=email, 
            phone=phone, 
            user_type=user_type, 
            first_login_ip=request.META.get('REMOTE_ADDR') if request else None, 
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, request=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        return self.create_user(email, password, phone=None, request=request, **extra_fields)

class CustomUser(AbstractBaseUser):
    phone = models.CharField(max_length=15)

    unique_user_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    
    first_name = models.CharField(max_length=225)
    last_name = models.CharField(max_length=225)
    user_type = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('user', 'User')])
    is_active = models.CharField(max_length=10, choices=[('active', 'Active'), ('in_active', 'In_active')])
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    username = models.CharField(max_length=80, unique=False, blank=True, null=True)
    email = models.EmailField(max_length=80, unique=True)
    
    # New fields to store the user's IP addresses
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    first_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # New fields to track the number of devices
    tracked_devices_count = models.IntegerField(default=0)
    registered_devices_count = models.IntegerField(default=0)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

# Signal to capture IP on login
@receiver(user_logged_in)
def update_last_login_ip(sender, request, user, **kwargs):
    user.last_login_ip = request.META.get('REMOTE_ADDR')
    user.save()
