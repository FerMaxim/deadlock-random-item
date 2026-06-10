import json
from channels.generic.websocket import AsyncWebsocketConsumer

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = 'room_%s' % self.room_code
        self.nickname = None

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if self.nickname:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'room_message',
                    'data': {
                        'type': 'leave',
                        'nickname': self.nickname
                    }
                }
            )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if data.get('type') == 'join':
            self.nickname = data.get('nickname')
        
        # We just broadcast the exact same data to everyone else in the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'room_message',
                'data': data
            }
        )

    # Receive message from room group
    async def room_message(self, event):
        data = event['data']

        # Send message to WebSocket
        await self.send(text_data=json.dumps(data))
