import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Channel, Message
from django.contrib.auth.models import User, AnonymousUser
import urllib.parse

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check authentication
        if isinstance(self.scope["user"], AnonymousUser):
            await self.close(code=4001)
            return

        # Get channel ID from URL
        try:
            self.channel_id = int(self.scope['url_route']['kwargs']['channel_name'])
            self.room_group_name = f'chat_{self.channel_id}'
        except (ValueError, TypeError):
            await self.close(code=4002)  # Invalid channel ID
            return

        # Verify channel exists and user is a member
        channel = await self.get_channel()
        if not channel:
            await self.close(code=4002)  # Channel not found
            return
            
        if not await self.is_channel_member(channel):
            await self.close(code=4003)  # Not a member
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Send welcome message
        await self.send(text_data=json.dumps({
            'message': f'Hoş geldiniz, {self.scope["user"].username}!',
            'username': 'System'
        }))

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            if close_code == 4001:
                await self.send(text_data=json.dumps({
                    'error': 'Oturum açmanız gerekiyor.'
                }))
            elif close_code == 4002:
                await self.send(text_data=json.dumps({
                    'error': 'Kanal bulunamadı.'
                }))
            elif close_code == 4003:
                await self.send(text_data=json.dumps({
                    'error': 'Bu kanala erişim izniniz yok.'
                }))

    async def receive(self, text_data):
        try:
            if isinstance(self.scope["user"], AnonymousUser):
                await self.send(text_data=json.dumps({
                    'error': 'Oturum açmanız gerekiyor.'
                }))
                return

            text_data_json = json.loads(text_data)
            message = text_data_json['message'].strip()
            
            if not message:
                await self.send(text_data=json.dumps({
                    'error': 'Boş mesaj gönderilemez.'
                }))
                return

            username = self.scope["user"].username

            # Save message to database
            channel = await self.get_channel()
            if channel and await self.is_channel_member(channel):
                await self.save_message(channel, message)

                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'username': username
                    }
                )
            else:
                await self.send(text_data=json.dumps({
                    'error': 'Bu kanala mesaj gönderme izniniz yok.'
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Geçersiz mesaj formatı.'
            }))
        except KeyError:
            await self.send(text_data=json.dumps({
                'error': 'Mesaj içeriği gerekli.'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': 'Mesaj gönderilirken bir hata oluştu.'
            }))

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @database_sync_to_async
    def get_channel(self):
        try:
            return Channel.objects.get(id=self.channel_id)
        except Channel.DoesNotExist:
            return None

    @database_sync_to_async
    def is_channel_member(self, channel):
        return channel.members.filter(id=self.scope["user"].id).exists()

    @database_sync_to_async
    def save_message(self, channel, message):
        Message.objects.create(
            channel=channel,
            sender=self.scope["user"],
            content=message
        )