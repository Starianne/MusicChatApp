import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, ChatMember, Message

#let database access be async so it does not slow down rest of app
@database_sync_to_async
def save_message(chat_id, user, content):
    chat = Chat.objects.get(id = chat_id)
    return Message.objects.create(
        chat = chat,
        sender = user,
        content = content
    )

@database_sync_to_async
def is_chat_member(user, chat_id):
    return ChatMember.objects.filter(chat_id = chat_id, user = user).exists()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.chat_id}"
        user = self.scope["user"]

        #checks is user is logged in to make a connection
        if not user.is_authenticated:
            await self.close()
            return
        
        #check is user is member
        if not await is_chat_member(user, self.chat_id):
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json["message"]

        message = await save_message(self.chat_id, self.scope["user"], content)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message.content, "username": self.scope["user"].username, "created_at": message.created_at.isoformat()}
        )

    # Receive message from room group
    async def chat_message(self, event):

        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))