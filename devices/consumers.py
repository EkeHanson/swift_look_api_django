from channels.generic.websocket import AsyncWebsocketConsumer
import json

class DeviceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("device_notifications", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("device_notifications", self.channel_name)

    async def link_clicked(self, event):
        message = event["message"]
        data = event["data"]
        await self.send(json.dumps({
            "message": message,
            "data": data,
        }))
