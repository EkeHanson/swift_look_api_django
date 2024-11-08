from rest_framework import viewsets
from rest_framework.views import APIView
from users.models import CustomUser
from .serializers import UserSerializer, DeviceSerializer
from rest_framework import viewsets
from devices.models import Device
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework import viewsets, filters
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q  # Import Q for complex queries
from rest_framework import viewsets
from rest_framework.views import APIView
from users.models import CustomUser
from rest_framework.pagination import PageNumberPagination
from .serializers import UserSerializer, DeviceSerializer
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework import filters
from django.db.models import Q  # Import Q for complex queries

class UserPagination(PageNumberPagination):
    page_size = 15  # Override the page size specifically for this viewset


class DeviceSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        devices = Device.objects.filter(name__icontains=query)
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)
 

class UserSearchView(APIView):
    permission_classes = [AllowAny]  # Anyone can search
    

    def get(self, request):
        query = request.query_params.get('q', '')  # Get the search query from request
        if query:
            # Search users by email, first_name, or last_name
            users = CustomUser.objects.filter(
                Q(email__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).order_by('-date_joined')  # Order by date_joined descending
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No search query provided"}, status=status.HTTP_400_BAD_REQUEST)


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    pagination_class = UserPagination  # Use custom pagination
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    # queryset = CustomUser.objects.all().order_by('-date_joined')  # Ensure newest users come first
    queryset = CustomUser.objects.all()  # Ensure newest users come first
    serializer_class = UserSerializer
    pagination_class = UserPagination  # Use custom pagination
    permission_classes = [AllowAny]

    filter_backends = [filters.SearchFilter]  # Add the SearchFilter backend
    search_fields = ['email', 'first_name', 'last_name']  # Allow search by email, first_name, or last_name

    filterset_fields = ['is_active', 'user_type', 'created_ip', 'email']
    ordering_fields = ['date_joined', 'email', 'last_login']
    ordering = ['-date_joined']  # Default ordering (newest first)

    @action(detail=True, methods=['post'], url_path='suspend')
    def suspend_user(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'user suspended'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='reactivate')
    def reactivate_user(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'user reactivated'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        user = self.get_object()
        user.send_password_reset_email()
        return Response({'status': 'password reset email sent'}, status=status.HTTP_200_OK)
