from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Device
from .serializers import DeviceSerializer, DeviceSummarySerializer

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
