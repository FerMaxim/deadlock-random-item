import json
from channels.generic.websocket import AsyncWebsocketConsumer

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'room_{self.room_code}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # We just broadcast whatever JSON we receive to everyone else in the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'room_message',
                'message': data,
                'sender_channel': self.channel_name
            }
        )

    async def room_message(self, event):
        message = event['message']
        sender_channel = event['sender_channel']

        # Don't send the message back to the original sender
        if self.channel_name != sender_channel:
            await self.send(text_data=json.dumps(message))
