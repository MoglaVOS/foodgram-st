from rest_framework import serializers
from djoser.serializers import (
    UserSerializer as DjoserUserSerializer
)
from drf_extra_fields.fields import Base64ImageField
from api.models import User


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, label='Аватар')

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if request and request.user.is_authenticated:
            return request.user.authors.filter(author=obj).exists()
        return False
