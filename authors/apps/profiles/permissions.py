from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    This method allows only the owner of a profile to edit it
    """

    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            return obj.user == request.user
