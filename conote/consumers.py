import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model

User = get_user_model()


class OnlineUserConsumer(WebsocketConsumer):

    def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            self.close()

        self.user_group_name = f"user_{self.user.id}"

        async_to_sync(self.channel_layer.group_add)(
            self.user_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.user_group_name, self.channel_name
        )
        pass

    def receive(self, text_data=None, bytes_data=None):
        pass

    def send_message(self, value):
        self.send(text_data=json.dumps(value))
