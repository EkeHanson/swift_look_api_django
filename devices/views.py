from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Device
from .serializers import DeviceSerializer, DeviceSummarySerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import DeviceSerializer

class UserDeviceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Fetch devices associated with the logged-in user
        user = request.user
        devices = Device.objects.filter(user=user)
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']  # Ensure 'post' is included

    def create(self, request, *args, **kwargs):
        print(request.method)  # Log method to ensure 'POST' is being received
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def get_serializer_class(self):
        # Use UserSummarySerializer for GET requests
        if self.action == 'retrieve' or self.action == 'list':
            return DeviceSummarySerializer  # DeviceSerializer with user info
        return DeviceSerializer  # Default serializer for POST, PUT, etc.


