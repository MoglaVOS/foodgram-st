from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from api.models import CustomUser as User
from api.serializers.recipes import UserRecipeSerializer


class CustomUserViewSet(UserViewSet):
    """Кастомный UserViewSet."""
    lookup_url_kwarg = 'pk'

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        user = self.request.user
        serializer = self.get_serializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            if user == author:
                raise ValidationError('Нельзя подписаться на самого себя.')
            obj, is_created = user.subscriptions.get_or_create(author=author)
            if not is_created:
                raise ValidationError('Вы уже подписаны.')
            serializer = UserRecipeSerializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            obj = user.subscriptions.filter(author=author)
            if not obj.exists():
                raise ValidationError('Вы не подписаны.')
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(author__subscriber=user)
        page = self.paginate_queryset(queryset)
        serializer = UserRecipeSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['put', 'delete'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='me/avatar'
            )
    def set_avatar(self, request):
        if request.method == 'PUT':
            if 'avatar' not in request.data:
                return Response({'detail': 'Поле обязательно'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response({'avatar': serializer.data['avatar']},
                                status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'DELETE':
            request.user.avatar.delete()
            request.user.avatar = None
            request.user.save()
            return Response({'detail': 'Аватар успешно удален'},
                            status=status.HTTP_204_NO_CONTENT)
