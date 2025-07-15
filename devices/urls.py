from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet, GenerateTrackableLinkView, track_link, UserDeviceViewSet
from .consumers import DeviceConsumer

router = DefaultRouter()
router.register(r'devices', DeviceViewSet)
router.register(r'user-devices', UserDeviceViewSet, basename='user-devices')

urlpatterns = [
    path('', include(router.urls)),
    path('generate-link/', GenerateTrackableLinkView.as_view(), name='generate-link'),
    path('track-link/<int:device_id>/', track_link, name='track-link'),
    #path('trackable-link-status/<int:device_id>/', TrackableLinkStatusView.as_view(), name='trackable-link-status'),
    
]

websocket_urlpatterns = [
    path('ws/device/<int:device_id>/', DeviceConsumer.as_asgi()),
]


















# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import DeviceViewSet, UserDeviceViewSet, GenerateTrackableLinkView, track_link, TrackableLinkStatusView

# router = DefaultRouter()
# router.register(r'devices', DeviceViewSet)
# router.register(r'user-devices', UserDeviceViewSet, basename='user-devices')

# urlpatterns = [
#     path('', include(router.urls)),
#     path('api/generate-link/', GenerateTrackableLinkView.as_view(), name='generate-link'),
#     path('track-link/<int:device_id>/', track_link, name='track-link'),
#     path('api/trackable-link-status/<int:device_id>/', TrackableLinkStatusView.as_view(), name='trackable-link-status'),
# ]


