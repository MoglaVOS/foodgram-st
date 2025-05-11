from django.contrib.auth import get_user_model
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404

from djoser.views import UserViewSet

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination

from api.models import Follow
from api.serializers import CustomUserSerializer, FollowSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = self.request.user
        serializer = CustomUserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(User, pk=self.kwargs.get('pk'))
        if request.method == 'POST':
            serializer = FollowSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(user=request.user, following=author)
                return Response({f'Вы подписались на {author}': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'error': 'Объект не найден'}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            deleted, _ = Follow.objects.filter(user=request.user, following=author).delete()
            if deleted:
                return Response({'detail': 'Успешная отписка'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'detail': 'Подписка не найдена'}, status=status.HTTP_400_BAD_REQUEST)
