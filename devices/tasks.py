from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_tracking_email(recipient_email, unique_link, device_name):
    send_mail(
        subject="Track Your Lost Device",
        message=f"Hello,\n\nClick the link to track your device ({device_name}):\n\n{unique_link}\n\nBest regards,\nSwiftLook Team",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        fail_silently=False,
    )

from celery import shared_task

@shared_task
def send_sms_notification(phone_number):
    print(f"Sending SMS to {phone_number}")
    return True
