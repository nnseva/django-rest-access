[![Build Status](https://travis-ci.com/nnseva/django-rest-access.svg)](https://travis-ci.com/nnseva/django-rest-access)

# Django-REST-Access

The Django-REST-Access package provides a permissions backend for the [Django REST Framework](https://www.django-rest-framework.org)
using access rules defined by the [Django-Access](https://github.com/nnseva/django-access) package.

## Installation

*Stable version* from the PyPi package repository
```bash
pip install django-rest-access
```

*Last development version* from the GitHub source version control system
```bash
pip install git+git://github.com/nnseva/django-rest-access.git
```

## Configuration

Include the `rest_framework`, `access`, and `rest_access` applications into the `INSTALLED_APPS` list, like:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    ...
    'rest_framework',
    'access',
    'rest_access',
    ...
]
```

## Using

### Define access rules

Define access rules as it is described in the [Django-Access](https://github.com/nnseva/django-access) package documentation.

### Serializer Mixin

Use `rest_access.access.AccessSerializerMixin` as a first of base classes for every Serializer in your API description which
should be controlled by access rules defined using [Django-Access](https://github.com/nnseva/django-access) package, like:

```python
from rest_framework import serializers, viewsets
from rest_access.access import AccessSerializerMixin
from django.contrib.auth.models import User, Group

...

class GroupSerializer(AccessSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'id', 'name')
```

### Authorization backend to use

The authorization backend `rest_access.access.AccessPermission` should be used as the both,
permission control backend and filtering class.

The `rest_access.access.AccessPermission` can be used together with other
permission control backends and filtering classes without restrictions.

#### Using authorization backend individually for selected model views

You can assign a permissions control backend and filtering class for the sole, or some subset of model views
or viewsets like it is described in the
[Django REST Framework permission documentation](https://www.django-rest-framework.org/api-guide/permissions/)
and [Django REST Framework filtering documentation](https://www.django-rest-framework.org/api-guide/filtering/)
correspondingly:

```python
from rest_framework import serializers, viewsets
...

class SomeModelViewSet(viewsets.ModelViewSet):
    ...
    permission_classes = ['rest_access.access.AccessPermission']
    filter_backends = ['rest_access.access.AccessPermission']
```

#### Using authorization backend as a default one

You can assign a permission control backend and filtering class as default ones for all views in the project using settings module
as it is described in the [Django REST Framework settings documentation](https://www.django-rest-framework.org/api-guide/settings/):

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_access.access.AccessPermission'
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'rest_access.access.AccessPermission'
    ],
}
```
