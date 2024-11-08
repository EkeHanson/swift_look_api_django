from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, DeviceViewSet, UserSearchView, DeviceSearchView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'devices', DeviceViewSet)
# router.register(r'tracking_histories', TrackingHistoryViewSet)
# router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('search-users/', UserSearchView.as_view(), name='search-users'),  # New URL for search
    path('search-devices/', DeviceSearchView.as_view(), name='search-devices'),
]