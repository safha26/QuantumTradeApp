import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OrderBookConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']

        await self.channel_layer.group_add("orderbook", self.channel_name)

        if self.user.is_authenticated:
            user_group = f'user_{self.user.id}'
            await self.channel_layer.group_add(user_group, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("orderbook", self.channel_name)

        if self.user.is_authenticated:
            user_group = f'user_{self.user.id}'
            await self.channel_layer.group_discard(user_group, self.channel_name)

    async def receive(self, text_data):
        pass

    async def order_book_update(self, event):t
        await self.send(text_data=json.dumps(event["data"]))

    async def user_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_notification',
            'message': event['message'],
        }))