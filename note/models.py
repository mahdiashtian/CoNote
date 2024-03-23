from django.contrib.auth import get_user_model
from django.db import models

from note.abstract_models import BaseModel

User = get_user_model()


class NoteBook(BaseModel):
    title = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return self.title


class Note(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    placement = models.IntegerField()
    notebook = models.ForeignKey(NoteBook, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class BookMark(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.note.title}"


class Comment(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.note.title}"
