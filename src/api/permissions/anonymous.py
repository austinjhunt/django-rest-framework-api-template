# Path: api/permissions/anonymous.py

from rest_framework import permissions

class IsAnonymous(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_anonymous