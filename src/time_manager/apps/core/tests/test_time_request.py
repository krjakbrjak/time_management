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
        self.url = reverse('core:time-list')
        self.password = 'password'
        self.user = get_user_model().objects.create_user('user', password=self.password)
        self.profile = Profile.objects.create(user=self.user)
        self.profile.save()
        self.user.save()
        self.token = Token.objects.create(user=self.user).key

    def test_create_request(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        # Testing if requests can be created
        count = 10
        for i in range(count):
            timestamp = datetime.now()
            response = self.client.post(self.url, data={
                'start': timestamp
            }, format='json')

            data = json.loads(response.content)
            serializer = TimeReadSerializer(data=data)
            self.assertTrue(serializer.is_valid())

            result = parse(data['start'], ignoretz=True)
            self.assertEqual(timestamp, result)

        response = self.client.get(self.url)
        self.assertEqual(len(response.data), count)

        # Testing if requests might be edit
        response = self.client.patch(reverse('core:time-detail', kwargs={'pk': 1}), {
            'start': datetime.fromtimestamp(0)
        })
        result = parse(response.data['start'], ignoretz=True)

        self.assertEqual(datetime.fromtimestamp(0), result)

        # Testing if requests might be removed
        response = self.client.delete(reverse('core:time-detail', kwargs={'pk': 1}))
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), count - 1)
