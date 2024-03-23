from guardian.shortcuts import get_objects_for_user
from rest_framework import serializers

from note.models import Note, NoteBook


class SpecificationField(serializers.PrimaryKeyRelatedField):
    specification = None
    model = None

    @property
    def target(self):
        return None

    @property
    def extra_queryset(self):
        return self.model.objects.none()

    def get_queryset(self):
        user = self.context.get('request').user
        if user.is_superuser:
            return self.model.objects.all()
        return self.model.objects.filter(**{self.specification: self.target}) | self.extra_queryset


class UserSpecificNoteField(SpecificationField):
    specification = 'notebook__user'
    model = Note

    @property
    def target(self):
        request = self.context.get('request')
        return request.user


class UserSpecificNoteBookField(SpecificationField):
    specification = 'user'
    model = NoteBook

    @property
    def target(self):
        request = self.context.get('request')
        return request.user


class UserSpecificBookMarkField(SpecificationField):
    specification = 'notebook__user'
    model = Note

    @property
    def extra_queryset(self):
        perm = "note.view_notebook"
        request = self.context['request']
        user = request.user
        notebook_user = NoteBook.objects.filter(user=user)
        notebook_perm = get_objects_for_user(user, perm, klass=NoteBook)
        queryset = self.model.objects.filter(notebook__in=notebook_user | notebook_perm)
        return queryset

    @property
    def target(self):
        request = self.context.get('request')
        return request.user


class UserSpecificCommentField(UserSpecificBookMarkField):
    ...
