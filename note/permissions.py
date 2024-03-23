from guardian.shortcuts import get_objects_for_user
from rest_framework.permissions import BasePermission

from note.models import NoteBook, Note


class IsOwnerOrHasPerm(BasePermission):
    def has_permission(self, request, view):
        perm = "note.view_notebook"
        user = request.user
        notebook = request.query_params.get('notebook', None)
        notebook_user = NoteBook.objects.filter(user=user)
        notebook_perm = get_objects_for_user(user, perm, klass=NoteBook)
        queryset = notebook_user | notebook_perm
        has_perm = queryset.filter(id=notebook).exists()
        return bool(
            has_perm or request.method in ['POST']
        )


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj: Note):
        user = request.user
        if hasattr(obj, 'user'):
            return obj.user == user
        if hasattr(obj, 'notebook'):
            return obj.notebook.user == user
