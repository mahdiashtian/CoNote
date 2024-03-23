from rest_framework import permissions


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class IsCurrentUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj
