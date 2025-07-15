
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.timezone import now
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import user_agents
from django.http import HttpResponse
import requests
from .models import Device, TrackableLink
from .serializers import DeviceSerializer, DeviceSummarySerializer, GenerateLinkSerializer
from rest_framework.throttling import UserRateThrottle

class DeviceRateThrottle(UserRateThrottle):
    rate = '100/hour'

def get_geolocation(ip_address):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def track_link(request, device_id):
    link = get_object_or_404(TrackableLink, device_id=device_id)
    ip_address = get_client_ip(request)
    raw_user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    try:
        parsed_ua = user_agents.parse(raw_user_agent)
        browser = f"{parsed_ua.browser.family} {parsed_ua.browser.version_string}"
        os = f"{parsed_ua.os.family} {parsed_ua.os.version_string}"
        device_type = 'Mobile' if parsed_ua.is_mobile else 'Tablet' if parsed_ua.is_tablet else 'PC'
    except Exception:
        browser, os, device_type = "Unknown", "Unknown", "Unknown"

    geolocation_data = get_geolocation(ip_address)
    
    link.is_clicked = True
    link.clicked_at = now()
    link.ip_address = ip_address
    link.user_agent = raw_user_agent
    link.browser = browser
    link.device_type = device_type
    link.os_info = os
    link.geolocation = geolocation_data
    link.save()

    # Update device location
    if geolocation_data:
        device = link.device
        device.latitude = geolocation_data.get('lat')
        device.longitude = geolocation_data.get('lon')
        device.city = geolocation_data.get('city')
        device.state = geolocation_data.get('regionName')
        device.postal_code = geolocation_data.get('zip')
        device.is_tracked = True
        device.last_online = now()
        device.save()

    # Send WebSocket notification
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"device_{device_id}",
            {
                "type": "device_update",
                "message": f"Device {link.device.name} location updated.",
                "data": {
                    "device_id": device_id,
                    "name": link.device.name,
                    "latitude": geolocation_data.get('lat') if geolocation_data else None,
                    "longitude": geolocation_data.get('lon') if geolocation_data else None,
                    "city": geolocation_data.get('city') if geolocation_data else None,
                    "timestamp": str(now()),
                },
            }
        )
    except Exception as e:
        print(f"WebSocket error: {str(e)}")

    return HttpResponse("Link clicked and tracked.")

class GenerateTrackableLinkView(APIView):
    serializer_class = GenerateLinkSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [DeviceRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        device_id = serializer.validated_data['device_id']
        recipient_email = request.data.get('email')

        if not recipient_email:
            return Response({"error": "Recipient email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(id=device_id, user=request.user)
        except Device.DoesNotExist:
            return Response({"error": "Device not found or not owned by user"}, status=status.HTTP_404_NOT_FOUND)

        trackable_link = TrackableLink.objects.filter(device=device).first()
        if trackable_link:
            unique_link = trackable_link.link
        else:
            unique_link = request.build_absolute_uri(reverse('track-link', kwargs={'device_id': device.id}))
            trackable_link = TrackableLink.objects.create(device=device, link=unique_link)

        # Send email asynchronously using Celery
        try:
            from .tasks import send_tracking_email
            send_tracking_email.delay(recipient_email, unique_link, device.name)
        except Exception as e:
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {
                "message": "Trackable link emailed successfully.",
                "link": unique_link,
                "status": "existing" if trackable_link.clicked_at else "new",
            },
            status=status.HTTP_200_OK if trackable_link.clicked_at else status.HTTP_201_CREATED
        )

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all().order_by('-registration_date')
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [DeviceRateThrottle]

    def get_queryset(self):
        return Device.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return DeviceSummarySerializer
        return DeviceSerializer
    
class UserDeviceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        devices = Device.objects.filter(user=user)
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)


























# from rest_framework.response import Response
# from rest_framework import status, viewsets
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from .models import Device
# from .serializers import DeviceSerializer, DeviceSummarySerializer
# from django.shortcuts import get_object_or_404
# from django.urls import reverse
# from .models import Device, TrackableLink
# from .serializers import GenerateLinkSerializer
# from django.http import HttpResponse
# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer
# from django.utils.timezone import now
# from .models import TrackableLink
# from rest_framework.views import APIView
# from .models import Device, TrackableLink
# from django.core.mail import send_mail
# from django.conf import settings

# import user_agents
# import requests

# def get_geolocation(ip_address):
#     try:
#         response = requests.get(f"http://ip-api.com/json/{ip_address}")
#         if response.status_code == 200:
#             return response.json()  # Returns geolocation data as a dictionary
#     except Exception as e:
#         return None


# # def get_geolocation(ip_address):
# #     IPStack_ACCESS_KEY = 'dac5d74b4ffd3852ba3d516b7802a753'


# #     try:
# #         response = requests.get(f"https://api.ipstack.com/{ip_address}?access_key={IPStack_ACCESS_KEY}")
# #         if response.status_code == 200:
# #             data = response.json()
# #             print("Geolocation Data:", data)
# #             return data
        
# #     except Exception as e:
# #         print("An error occurred while fetching geolocation data:", e)
# #         return None




# class TrackableLinkStatusView(APIView):
#     """
#     View to check the status of a TrackableLink object.
#     """
#     permission_classes = [AllowAny]  # Ensure only authenticated users can access

#     def get(self, request, device_id, *args, **kwargs):
#         """
#         Get the tracking status of a specific link associated with a device.
#         """
#         try:
#             # Fetch the TrackableLink object for the given device_id
#             trackable_link = TrackableLink.objects.filter(device__id=device_id).first()

#             if not trackable_link:
#                 return Response(
#                     {"error": "No trackable link found for the provided device ID."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             # Access the related device object
#             device = trackable_link.device

#             # Prepare the response data
#             data = {
#                 "device_name": device.name,
#                 "device_id": device.id,
#                 "link": trackable_link.link,
#                 "is_clicked": trackable_link.is_clicked,
#                 "clicked_at": trackable_link.clicked_at,
#                 "ip_address": trackable_link.ip_address,
#                 "user_agent": trackable_link.user_agent,
#                 "browser": trackable_link.browser,
#                 "device_type": trackable_link.device_type,
#                 "os_info": trackable_link.os_info,
#                 "geolocation": trackable_link.geolocation,
#             }

#             return Response(data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response(
#                 {"error": f"An error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )


# def get_client_ip(request):
#     """Extracts client IP address."""
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     return ip

# def track_link(request, device_id):
#     """Handles tracking of link clicks."""
#     link = get_object_or_404(TrackableLink, device_id=device_id)  # Corrected line

#     # Extract user agent and IP address
#     raw_user_agent = request.META.get('HTTP_USER_AGENT', '')
#     ip_address = get_client_ip(request)

#     # Parse user agent details
#     try:
#         parsed_ua = user_agents.parse(raw_user_agent)
#         browser = f"{parsed_ua.browser.family} {parsed_ua.browser.version_string}"
#         os = f"{parsed_ua.os.family} {parsed_ua.os.version_string}"
#         device_type = 'Mobile' if parsed_ua.is_mobile else 'Tablet' if parsed_ua.is_tablet else 'PC'
#     except Exception:
#         browser, os, device_type = "Unknown", "Unknown", "Unknown"

#     # Fetch geolocation data
#     geolocation_data = get_geolocation(ip_address)

#     # Update tracking details
#     link.is_clicked = True
#     link.clicked_at = now()
#     link.ip_address = ip_address
#     link.user_agent = raw_user_agent
#     link.browser = browser
#     link.device_type = device_type
#     link.language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
#     link.geolocation = geolocation_data

#     link.save()

#     # Send WebSocket notification (if configured)
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         "device_notifications",
#         {
#             "type": "link_clicked",
#             "message": f"Link for device {link.device.name} clicked.",
#             "data": {
#                 "device": link.device.name,
#                 "clicked_at": str(link.clicked_at),
#                 "ip_address": link.ip_address,
#                 "browser": browser,
#                 "os": os,
#                 "device_type": device_type,
#                 "geolocation": geolocation_data,
#             },
#         }
#     )

#     return HttpResponse("Link clicked successfully.")


# class GenerateTrackableLinkView(APIView):
#     serializer_class = GenerateLinkSerializer
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         device_id = request.data.get("device_id")
#         recipient_email = request.data.get("email")  # Email of the recipient

#         if not device_id:
#             return Response({"error": "Device ID is required"}, status=status.HTTP_400_BAD_REQUEST)

#         if not recipient_email:
#             return Response({"error": "Recipient email is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Get the device
#             device = Device.objects.get(id=device_id)
#         except Device.DoesNotExist:
#             return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

#         # Check if a trackable link already exists for this device
#         trackable_link = TrackableLink.objects.filter(device=device).first()
#         if trackable_link:
#             # If the link already exists, email it and return
#             unique_link = trackable_link.link
#         else:
#             # Generate a new trackable link
#             unique_link = request.build_absolute_uri(
#                 reverse('track-link', kwargs={'device_id': device.id})
#             )
#             trackable_link = TrackableLink.objects.create(device=device, link=unique_link)

#         # Send the link via email
#         try:
#             send_mail(
#                 subject="Trackable Link for Your Device",
#                 message=f"Hello,\n\nClick the link below to track your device:\n\n{unique_link}\n\nBest regards,\nYour Team",
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[recipient_email],
#                 fail_silently=False,
#             )
#         except Exception as e:
#             return Response(
#                 {"error": f"Failed to send email: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#         # Return the link with a message indicating whether it was reused or newly created
#         return Response(
#             {
#                 "message": "Trackable link emailed successfully.",
#                 "link": unique_link,
#                 "status": "existing" if trackable_link.clicked_at else "new",
#             },
#             status=status.HTTP_200_OK if trackable_link.clicked_at else status.HTTP_201_CREATED
#         )

#     def delete(self, request, *args, **kwargs):
#         device_id = request.data.get("device_id")

#         if not device_id:
#             return Response({"error": "Device ID is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Get the trackable link for the device
#             trackable_link = TrackableLink.objects.get(device_id=device_id)
#             trackable_link.delete()  # Delete the trackable link
#             return Response(
#                 {"message": "Trackable link deleted successfully."},
#                 status=status.HTTP_200_OK
#             )
#         except TrackableLink.DoesNotExist:
#             return Response(
#                 {"error": "Trackable link not found for the provided device ID."},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             return Response(
#                 {"error": f"An error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )





# class UserDeviceViewSet(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]

#     def list(self, request):
#         # Fetch devices associated with the logged-in user
#         user = request.user
#         devices = Device.objects.filter(user=user)
#         serializer = DeviceSerializer(devices, many=True)
#         return Response(serializer.data)

# class DeviceViewSet(viewsets.ModelViewSet):
#     queryset = Device.objects.all().order_by('id') 
#     serializer_class = DeviceSerializer
#     permission_classes = [AllowAny]
#     http_method_names = ['get', 'post', 'put', 'patch', 'delete']

#     def create(self, request, *args, **kwargs):
#         print(request.method)
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def get_serializer_class(self):
#         if self.action in ['retrieve', 'list']:
#             return DeviceSummarySerializer  # DeviceSerializer with user info
#         return DeviceSerializer  # Default serializer for POST, PUT, etc.
