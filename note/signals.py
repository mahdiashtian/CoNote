from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from note.models import Comment


@receiver(post_save, sender=Comment)
def comment_post_save(sender, instance: Comment, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{instance.note.notebook.user}', {
                'type': 'comment_message',
                'message': f"{instance.user.username} commented on {instance.note.title}"
            }
        )
