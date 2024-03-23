from django_filters.rest_framework import DjangoFilterBackend
from guardian.shortcuts import get_objects_for_user
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from informing.models import Notification
from note.api.exceptions import NoteBookIsRequired
from note.api.serializers import NoteBookSerializer, NoteSerializer, BookMarkSerializer, CommentSerializer, \
    AssignPermSerializer
from note.models import NoteBook, Note, BookMark, Comment
from note.permissions import IsOwnerOrHasPerm, IsOwner


class NoteBookViewSet(viewsets.ModelViewSet):
    queryset = NoteBook.objects.all()
    serializer_class = NoteBookSerializer

    def get_queryset(self):
        user = self.request.user
        queryset_prem = get_objects_for_user(user, 'note.view_notebook', klass=NoteBook)
        queryset_user = self.queryset.filter(user=user)
        return queryset_prem | queryset_user

    def get_permissions(self):
        if self.action in ['destroy', 'update', 'partial_update', 'assign_perm', 'remove_perm']:
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(detail=True, methods=['post'], serializer_class=AssignPermSerializer)
    def assign_perm(self, request, pk=None):
        user = request.user
        instance: NoteBook = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_to = serializer.validated_data['user']
        Notification.objects.create(
            user=user_to,
            content=f'You have been assigned to a notebook {instance.title}',
            type=Notification.TypeChoices.INFO
        )
        Notification.objects.create(
            user=user,
            content=f'You have assigned a notebook {instance.title} to {user_to.username}',
            type=Notification.TypeChoices.WARNING
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], serializer_class=AssignPermSerializer)
    def remove_perm(self, request, pk=None):
        user = request.user
        instance: NoteBook = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_to = serializer.validated_data['user']
        Notification.objects.create(
            user=user_to,
            content=f'You have been removed from a notebook {instance.title}',
            type=Notification.TypeChoices.INFO
        )
        Notification.objects.create(
            user=user,
            content=f'You have removed a notebook {instance.title} from {user_to.username}',
            type=Notification.TypeChoices.WARNING
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['notebook']

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [IsAuthenticated, IsOwnerOrHasPerm]
        elif self.action == 'create':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated, IsOwner]
        return super().get_permissions()

    def filter_queryset(self, queryset):
        notebook = self.request.query_params.get('notebook', None)
        if notebook is None and self.action == 'list':
            raise NoteBookIsRequired
        return super().filter_queryset(queryset)


class BookMarkViewSet(viewsets.ModelViewSet):
    queryset = BookMark.objects.all()
    serializer_class = BookMarkSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['note__notebook', 'user']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return self.queryset.filter(
            user=user
        )


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['note__notebook', 'user']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return self.queryset.filter(
            user=user
        )
