from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Проверка на автора рецепта."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user
