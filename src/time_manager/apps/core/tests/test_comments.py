from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token
from rest_framework import status

from datetime import datetime
import json
from dateutil.parser import parse

from ..models import TimeRequest
from ..models import RequestType
from ..models import Profile
from ..serializers import TimeSerializer
from ..serializers import TimeReadSerializer

class TestTimeRequest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('core:comment-list')
        self.password = 'password'
        self.user = get_user_model().objects.create_user('user', password=self.password)
        self.profile = Profile.objects.create(user=self.user)
        self.profile.save()
        self.user.save()
        self.token = Token.objects.create(user=self.user).key

    def test_create_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        # create request
        response = self.client.post(reverse('core:time-list'), data={
            'start': datetime.now()
        }, format='json')
        request = response.data

        comment = f'This is a comment to {request["id"]} request by {request["user"]}'
        response = self.client.post(self.url, data={
            'request': request['id'],
            'comment': comment
        })

        # verify that the comment's user is the one who created the comment
        self.assertEqual(response.data['user'], self.profile.id)

        # verify that the comment's text is correct
        self.assertEqual(response.data['comment'], comment)

        comment = f'This is an updated comment to {request["id"]} request by {request["user"]}'
        response = self.client.patch(reverse('core:comment-detail', kwargs={'pk': response.data['id']}), data={
            'request': request['id'],
            'comment': comment
        })

        # verify that the comment's text is correct
        self.assertEqual(response.data['comment'], comment)
