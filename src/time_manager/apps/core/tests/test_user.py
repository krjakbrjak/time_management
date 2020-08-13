from django.test import TestCase
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token
from rest_framework import status

import json
import mimetypes

from ..models import ImageMimeType
from .helpers import create_image

class TestUserRequest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('core:profile-list')
        self.password = 'password'
        self.user = get_user_model().objects.create_user('user', password=self.password)
        self.user.is_admin = True
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.token = Token.objects.create(user=self.user).key

        mimetypes.init()

    def _create_user(self, username, password):
        response = self.client.post(self.url, data={
            'user': {
                'username': username,
                'password': password
            }
        }, format='json')

        return response

    def test_create_user_no_authorized(self):
        ''' Checks whether a user can be created by an authorized user.
        '''
        response = self._create_user('user1', 'password')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_create_user_no_admin(self):
        ''' Checks whether a user can be created by an authorized
        user, which is not an admin.
        '''
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        response = self._create_user('user1', 'password')
        content = json.loads(response.content)

        user = get_user_model().objects.get(username='user1')
        token = Token.objects.create(user=user).key

        # Try to create a user by a non-admin user
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self._create_user('user2', 'password')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_create_user_token(self):
        ''' Checks whether token is created when a new
        user is added. Token shouldn't be created, this is
        unnecessary since token is created during login procedure
        (if it does not exist yet).
        '''
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        response = self._create_user('user1', 'password')
        content = json.loads(response.content)

        token = True
        try:
            Token.objects.get(user__id=content['user']['id'])
        except Token.DoesNotExist as e:
            token = False

        self.assertFalse(token)

    def _update_avatar(self, pk, avatar_file):
        mt, _ = mimetypes.guess_type(avatar_file.name)

        ImageMimeType.objects.create(name=mt)

        response = self.client.patch(reverse('core:profile-detail', kwargs={'pk': pk}), data=encode_multipart(BOUNDARY, {
            'avatar': avatar_file,
        }), content_type=MULTIPART_CONTENT)
        content = json.loads(response.content)

        return self.client.get(content['avatar'])

    def test_update_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        response = self._create_user('user1', 'password')
        content = json.loads(response.content)
        pk = content['id']

        original = create_image(suffix='.jpg')
        response = self._update_avatar(pk, original)
        content = response.content

        # seek to the beginning since it was already read
        original.seek(0)
        self.assertEqual(original.read(), content)

        original = create_image(suffix='.pdf')
        response = self._update_avatar(pk, original)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_session(self):
        response = self.client.get(reverse('core:session'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(reverse('core:session'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['username'], self.user.username)
