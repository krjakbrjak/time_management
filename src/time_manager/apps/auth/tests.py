from django.test import TestCase
from django.contrib.auth import get_user_model
from django.http.cookie import SimpleCookie

from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token

import json

def test_login_correct_credentials(self):
    response = self.client.post(self.url, data={
        'username': self.user.username,
        'password': self.password
        }, format="json")
    try:
        db_entry = Token.objects.get(user=self.user)
        content = json.loads(response.content)
        token = response.cookies.get('Token', None)
    except:
        self.assertTrue(False, "Failed to login")
    else:
        self.token = token.value
        self.assertEqual(token.value, db_entry.key)
        self.assertEqual(content['user'], self.user.username)

class TestLoginRequest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('auth:login')
        self.password = 'password'
        self.user = get_user_model().objects.create_user('user', password=self.password)

    def test_login_nocredentials(self):
        response = self.client.post(self.url, data={}, format="json")
        content = json.loads(response.content)
        self.assertEqual(sorted(content['error'].keys()), ['password', 'username'])

    def test_login_wrong_credentials(self):
        response = self.client.post(self.url, data={
            'username': self.user.username,
            'password': '123',
            'aaa': 1
        }, format="json")
        content = json.loads(response.content)
        self.assertEqual(content['error'], 'Wrong credentials!')

    def test_logout_credentials_wrong_token(self):
        test_login_correct_credentials(self)
        self.client.cookies = SimpleCookie({'Token': '!!!!!!'})
        response = self.client.delete(self.url, data={
            'username': self.user.username,
            }, format="json")
        content = json.loads(response.content)

        count = Token.objects.filter(user=self.user).count()
        self.assertEqual(count, 1)

    def test_logout_credentials(self):
        test_login_correct_credentials(self)
        self.client.cookies = SimpleCookie({'Token': self.token})
        response = self.client.delete(self.url, data={
            'username': self.user.username,
            }, format="json")
        content = json.loads(response.content)

        count = Token.objects.filter(user=self.user).count()
        self.assertEqual(count, 0)

    def test_logout_no_credentials(self):
        test_login_correct_credentials(self)
        self.client.cookies = SimpleCookie({})
        response = self.client.delete(self.url, data={
            }, format="json")
        content = json.loads(response.content)

        self.assertEqual(content['detail'], 'Authentication credentials were not provided.')

        count = Token.objects.filter(user=self.user).count()
        self.assertEqual(count, 1)
