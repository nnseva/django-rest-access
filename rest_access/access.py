"""Django REST Framework permissions module using Django Access package"""
from __future__ import absolute_import

import collections

from rest_framework import permissions
from rest_framework import exceptions
from rest_framework import filters

from django.db.models.fields.related import ForeignObjectRel
from six import string_types

from access.managers import AccessManager


class Analyzer(object):
    """Analyze and extract request, view, and queryset parameters"""

    perms_map = {
        'GET': 'visible',
        'OPTIONS': 'visible',
        'HEAD': 'visible',
        'POST': 'appendable',
        'PUT': 'changeable',
        'PATCH': 'changeable',
        'DELETE': 'deleteable',
    }

    def get_view_queryset(self, request, view):
        """Returns view queryset, or None"""
        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
            if queryset is not None:
                return queryset
        if hasattr(view, 'queryset'):
            return view.queryset

    def get_queryset_model(self, request, queryset, view):
        """Returns a queryset model"""
        return queryset.model

    def get_requested_ability(self, request, queryset, view):
        """Returns a requested ability"""

        return self.perms_map.get(request.method, None)

    def filter_queryset(self, request, queryset, view):
        """Returns queryset filtered by access rights or None"""

        ability = self.get_requested_ability(request, queryset, view)
        if not ability:
            return

        return AccessManager(
            self.get_queryset_model(request, queryset, view)
        ).apply_able(ability, queryset, request)


class AccessFilter(Analyzer, filters.BaseFilterBackend):
    """
    Determines unconditional filtering basing on the Django Access.

    You can use this class or an ancestor one as a Filter Backend.
    """


class AccessPermission(AccessFilter, permissions.BasePermission):
    """
    Determines unconditional filtering and permission
    restrictions basing on the Django Access.

    Use this class as a Permission class, as well as a Filter Backend
    both by default for the whole project, or individually for separate models.
    """

    def has_permission(self, request, view):
        """
        Overriden to determine permissions to the whole model
        """
        # Workaround to ensure thet the AccessPermission is not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        queryset = self.get_view_queryset(request, view)

        if queryset is None:
            return False

        model = self.get_queryset_model(request, queryset, view)
        if not model:
            return False

        ability = self.get_requested_ability(request, queryset, view)
        if not ability:
            raise exceptions.MethodNotAllowed(request.method)

        return AccessManager(model).check_able(ability, model, request) is not False

    def has_object_permission(self, request, view, obj):
        """
        Overriden to determine permissions to the model instance
        """

        queryset = self.get_view_queryset(request, view)
        if queryset is None:
            return False

        model = self.get_queryset_model(request, queryset, view)
        if not model:
            return False

        ability = self.get_requested_ability(request, queryset, view)
        if not ability:
            raise exceptions.MethodNotAllowed(request.method)

        return bool(AccessManager(model).apply_able(ability, queryset, request).filter(pk=obj.pk))


class AccessSerializerMixin(object):
    """
    Implements Django Access object creation features
    """
    def create(self, validated_data):
        """Overriden to patch the object by the AccessManager-provided values"""
        ModelClass = self.Meta.model
        manager = AccessManager(ModelClass)
        data = manager.check_appendable(ModelClass, self.context['request'])
        if data is False:
            raise exceptions.PermissionDenied("Is not appendable")
        ret = super(AccessSerializerMixin, self).create(validated_data)
        if data:
            for k in data:
                v = data[k]
                fieldname = k
                if fieldname.endswith("_set"):
                    fieldname = fieldname[:-4]
                field = ret._meta.get_field(fieldname)
                if isinstance(field, ForeignObjectRel):
                    if isinstance(v, collections.Iterable) and not isinstance(v, string_types):
                        fld = getattr(ret, k)
                        for i in v:
                            fld.add(i)
                elif getattr(ret, k) is None:
                    setattr(ret, k, v)
            ret.save()
        return ret
