from __future__ import absolute_import

from django.contrib.auth.models import User, Group
from rest_framework import serializers, viewsets

from rest_access.access import AccessSerializerMixin

from api.router import router


class UserSerializer(AccessSerializerMixin, serializers.HyperlinkedModelSerializer):
    date_joined = serializers.DateTimeField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'date_joined')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_fields = ['first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
    ordering_fields = ['first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'date_joined']


router.register(r'user', UserViewSet)


class GroupSerializer(AccessSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'id', 'name')


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filterset_fields = ['name']
    ordering_fields = ['name']


router.register(r'group', GroupViewSet)
