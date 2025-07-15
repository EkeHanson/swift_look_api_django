from channels.generic.websocket import AsyncWebsocketConsumer
import json

class DeviceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        device_id = self.scope['url_route']['kwargs']['device_id']
        self.group_name = f"device_{device_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def device_update(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'data': event['data'],
        }))