from django.test import TestCase
from rest_framework.test import APIClient

from rest_framework.reverse import reverse
import json
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

class TestLoginRequest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('core:authorisation')
        self.password = 'password'
        self.user = get_user_model().objects.create_user('user', password=self.password)
        self.token = Token.objects.create(user=self.user).key

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

    def test_login_correct_credentials(self):
        response = self.client.post(self.url, data={
            'username': self.user.username,
            'password': self.password
            }, format="json")
        content = json.loads(response.content)
        self.assertEqual(content['token'], self.token)
        self.assertEqual(content['user'], self.user.username)

    def test_logout_no_credentials(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.delete(self.url, data={
            'username': self.user.username,
            }, format="json")
        content = json.loads(response.content)

        count = Token.objects.filter(user=self.user, key=self.token).count()
        self.assertEqual(count, 1)

    def test_logout_credentials(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.delete(self.url, data={
            'username': self.user.username,
            'token': self.token,
            }, format="json")
        content = json.loads(response.content)

        count = Token.objects.filter(user=self.user, key=self.token).count()
        self.assertEqual(count, 0)

    def test_logout_not_authorized(self):
        response = self.client.delete(self.url, data={
            }, format="json")
        content = json.loads(response.content)

        self.assertEqual(content['detail'], 'Authentication credentials were not provided.')
