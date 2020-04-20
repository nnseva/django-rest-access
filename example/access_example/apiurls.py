from __future__ import absolute_import

from django.conf.urls import include, url

from api.router import router
from api.api import *  # noqa

urlpatterns = [
    url(r'^v1/', include(router.urls)),
]
