from django.urls import path
from ..phone_tracker import consumers

websocket_urlpatterns = [
    path("ws/device-notifications/", consumers.DeviceConsumer.as_asgi()),
]
