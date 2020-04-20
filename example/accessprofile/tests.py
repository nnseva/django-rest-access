from __future__ import print_function

from django.test import TestCase as _TestCase
from django.test import Client

import json


class TestCase(_TestCase):
    if not hasattr(_TestCase, 'assertRegex'):
        assertRegex = _TestCase.assertRegexpMatches
    if not hasattr(_TestCase, 'assertNotRegex'):
        assertNotRegex = _TestCase.assertNotRegexpMatches


class TestBase(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User, Group, Permission
        from django.contrib import auth
        from django.contrib.contenttypes.models import ContentType
        from django.db.models import Model

        self.user = User.objects.create(username="test", is_active=True, is_staff=True)
        self.user.set_password("test")
        self.user.save()
        self.another = User.objects.create(username="another", is_active=True, is_staff=True)
        self.another.set_password("test")
        self.another.save()
        self.third = User.objects.create(username="third", is_active=True, is_staff=True)
        self.third.set_password("test")
        self.third.save()
        self.fourth = User.objects.create(username="fourth", is_active=True, is_staff=True)
        self.fourth.set_password("test")
        self.fourth.save()
        self.group = Group.objects.create(name="some")
        self.group.save()
        self.other_group = Group.objects.create(name="other")
        self.other_group.save()

        for cn in dir(auth.models):
            c = getattr(auth.models, cn)
            if isinstance(c, type) and issubclass(c, Model) and not c._meta.abstract and c._meta.app_label == 'auth':
                for cc in ['add', 'change', 'delete']:
                    self.user.user_permissions.add(
                        Permission.objects.get(
                            content_type=ContentType.objects.get(app_label=c._meta.app_label, model=c._meta.model_name),
                            codename='%s_%s' % (cc, c._meta.model_name),
                        )
                    )
                    self.group.permissions.add(
                        Permission.objects.get(
                            content_type=ContentType.objects.get(app_label=c._meta.app_label, model=c._meta.model_name),
                            codename='%s_%s' % (cc, c._meta.model_name),
                        )
                    )

        for cc in ['add', 'change', 'delete']:
            self.other_group.permissions.add(
                Permission.objects.get(
                    content_type=ContentType.objects.get(app_label='auth', model='user'),
                    codename='%s_%s' % (cc, 'user'),
                )
            )

        self.group.user_set.add(self.third)
        self.other_group.user_set.add(self.fourth)

    def tearDown(self):
        from django.contrib.auth.models import User, Group
        User.objects.all().delete()
        Group.objects.all().delete()


class FirstTest(TestBase):
    def test_1_login(self):
        c = Client()
        c.login(username='test', password='test')
        response = c.get('/api/v1/')
        self.assertEqual(response.status_code, 200)

    def test_2_login(self):
        c = Client()
        c.login(username='another', password='test')
        response = c.get('/api/v1/')
        self.assertEqual(response.status_code, 200)


class DjangoAccessTest(TestBase):
    def test_1_check_forbidden_django_permissions(self):
        c = Client()
        c.login(username='another', password='test')
        response = c.get('/api/v1/user/')
        self.assertNotEqual(response.status_code, 200)
        response = c.get('/api/v1/group/')
        self.assertNotEqual(response.status_code, 200)

    def test_2_check_allowed_django_user_permissions(self):
        c = Client()
        c.login(username='test', password='test')
        response = c.get('/api/v1/user/')
        self.assertEqual(response.status_code, 200)
        response = c.get('/api/v1/group/')
        self.assertEqual(response.status_code, 200)

    def test_3_check_allowed_django_group_permissions(self):
        c = Client()
        c.login(username='third', password='test')
        response = c.get('/api/v1/user/')
        self.assertEqual(response.status_code, 200)
        response = c.get('/api/v1/group/')
        self.assertEqual(response.status_code, 200)


class InstanceAccessTest(TestBase):
    def test_1_check_forbidden_instance_permissions(self):
        c = Client()
        c.login(username='test', password='test')
        response = c.get('/api/v1/group/')
        self.assertEqual(response.status_code, 200)
        response = c.patch('/api/v1/group/%s/' % self.group.id,
            content_type='application/json',
            data=json.dumps(dict(
                name='Test'
            ))
        )
        self.assertNotEqual(response.status_code, 202)

    def test_2_check_allowed_instance_permissions(self):
        c = Client()
        c.login(username='third', password='test')
        response = c.get('/api/v1/group/')
        self.assertEqual(response.status_code, 200)
        response = c.patch('/api/v1/group/%s/' % self.group.id,
            content_type='application/json',
            data=json.dumps(dict(
                name='Test'
            ))
        )
        self.assertEqual(response.status_code, 200)

    def test_3_check_allowed_instance_creation(self):
        c = Client()
        c.login(username='third', password='test')
        response = c.get('/api/v1/group/')
        self.assertEqual(response.status_code, 200)
        response = c.post('/api/v1/group/',
            content_type='application/json',
            data=json.dumps(dict(
                name='Test-additional'
            ))
        )
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 201)
        response = c.get('/api/v1/group/%s/' % data['id'])
        self.assertEqual(response.status_code, 200)
