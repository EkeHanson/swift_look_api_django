from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Device
from .serializers import DeviceSerializer, DeviceSummarySerializer
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Device, TrackableLink
from .serializers import GenerateLinkSerializer
from django.http import HttpResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils.timezone import now
from .models import TrackableLink
from rest_framework.views import APIView
from rest_framework import status
from django.urls import reverse
from .models import Device, TrackableLink
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse

class TrackableLinkStatusView(APIView):
    """
    View to check the status of a TrackableLink object.
    """
    permission_classes = [AllowAny]  # Ensure only authenticated users can access

    def get(self, request, device_id, *args, **kwargs):
        """
        Get the tracking status of a specific link associated with a device.
        """
        try:
            # Fetch the TrackableLink object for the given device_id
            trackable_link = TrackableLink.objects.filter(device__id=device_id).first()

            if not trackable_link:
                return Response(
                    {"error": "No trackable link found for the provided device ID."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Prepare the response data
            data = {
                "link": trackable_link.link,
                "is_clicked": trackable_link.is_clicked,
                "clicked_at": trackable_link.clicked_at,
                "ip_address": trackable_link.ip_address,
                "user_agent": trackable_link.user_agent,
            }

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def get_client_ip(request):
    """Extracts client IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def track_link(request, device_id):
    """Handles tracking of link clicks."""
    link = get_object_or_404(TrackableLink, device_id=device_id)
    
    # Update tracking details
    link.is_clicked = True
    link.clicked_at = now()
    link.ip_address = get_client_ip(request)
    link.user_agent = request.META.get('HTTP_USER_AGENT', '')
    link.save()

    # Send WebSocket notification (if WebSocket is configured)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "device_notifications",  # Channel group name
        {
            "type": "link_clicked",
            "message": f"Link for device {link.device.name} clicked.",
            "data": {
                "device": link.device.name,
                "clicked_at": str(link.clicked_at),
                "ip_address": link.ip_address,
            },
        }
    )
    return HttpResponse("Link clicked successfully.")




class GenerateTrackableLinkView(APIView):
    serializer_class = GenerateLinkSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        device_id = request.data.get("device_id")
        recipient_email = request.data.get("email")  # Email of the recipient

        if not device_id:
            return Response({"error": "Device ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not recipient_email:
            return Response({"error": "Recipient email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the device
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if a trackable link already exists for this device
        trackable_link = TrackableLink.objects.filter(device=device).first()
        if trackable_link:
            # If the link already exists, email it and return
            unique_link = trackable_link.link
        else:
            # Generate a new trackable link
            unique_link = request.build_absolute_uri(
                reverse('track-link', kwargs={'device_id': device.id})
            )
            trackable_link = TrackableLink.objects.create(device=device, link=unique_link)

        # Send the link via email
        try:
            send_mail(
                subject="Trackable Link for Your Device",
                message=f"Hello,\n\nClick the link below to track your device:\n\n{unique_link}\n\nBest regards,\nYour Team",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to send email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Return the link with a message indicating whether it was reused or newly created
        return Response(
            {
                "message": "Trackable link emailed successfully.",
                "link": unique_link,
                "status": "existing" if trackable_link.clicked_at else "new",
            },
            status=status.HTTP_200_OK if trackable_link.clicked_at else status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        device_id = request.data.get("device_id")

        if not device_id:
            return Response({"error": "Device ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the trackable link for the device
            trackable_link = TrackableLink.objects.get(device_id=device_id)
            trackable_link.delete()  # Delete the trackable link
            return Response(
                {"message": "Trackable link deleted successfully."},
                status=status.HTTP_200_OK
            )
        except TrackableLink.DoesNotExist:
            return Response(
                {"error": "Trackable link not found for the provided device ID."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

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
#             device = Device.objects.get(id=device_id)
#         except Device.DoesNotExist:
#             return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

#         # Generate the trackable link
#         unique_link = request.build_absolute_uri(
#             reverse('track-link', kwargs={'device_id': device.id})
#         )
#         trackable_link = TrackableLink.objects.create(device=device, link=unique_link)

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

#         return Response(
#             {
#                 "message": "Trackable link generated and emailed successfully.",
#                 "link": trackable_link.link
#             },
#             status=status.HTTP_201_CREATED
#         )
    




class UserDeviceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Fetch devices associated with the logged-in user
        user = request.user
        devices = Device.objects.filter(user=user)
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all().order_by('id') 
    serializer_class = DeviceSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        print(request.method)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return DeviceSummarySerializer  # DeviceSerializer with user info
        return DeviceSerializer  # Default serializer for POST, PUT, etc.
