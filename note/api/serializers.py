from django.contrib.auth import get_user_model
from guardian.shortcuts import assign_perm, remove_perm
from rest_framework import serializers

from note.api.fields import UserSpecificNoteBookField, UserSpecificBookMarkField, \
    UserSpecificCommentField
from note.models import NoteBook, Note, BookMark, Comment
from users.api.serializers import UserSerializer

User = get_user_model()


class NoteBookSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = NoteBook
        fields = '__all__'


class NoteSerializer(serializers.ModelSerializer):
    notebook = UserSpecificNoteBookField(queryset=NoteBook.objects.all())

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['comments'] = CommentSerializer(instance.comments.all(), many=True).data
        return data

    class Meta:
        model = Note
        fields = '__all__'


class BookMarkSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    note = UserSpecificBookMarkField(queryset=Note.objects.all())

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data
        return data

    class Meta:
        model = BookMark
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    note = UserSpecificCommentField(queryset=Note.objects.all())

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data
        return data

    class Meta:
        model = Comment
        fields = '__all__'


class AssignPermSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def save(self, **kwargs):
        notebook = self.context['view'].get_object()
        user = self.validated_data['user']
        perm = 'note.view_notebook'
        if self.context['view'].action == 'remove_perm':
            remove_perm(perm, user, notebook)
        else:
            assign_perm(perm, user, notebook)
        return self.validated_data
