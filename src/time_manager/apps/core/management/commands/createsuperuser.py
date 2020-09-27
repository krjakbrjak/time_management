from django.contrib.auth.management.commands import createsuperuser
from django.contrib.auth import get_user_model
from time_manager.apps.core.models import Profile

class Command(createsuperuser.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__over_input_data = {}

    def handle(self, *args, **kwargs):
        super().handle(*args, **kwargs)
        user = get_user_model().objects.get(username=self.__over_input_data['username'])
        Profile.objects.create(user=user)
    
    def get_input_data(self, field, message, default=None):
        data = super().get_input_data(field, message, default)
        self.__over_input_data[field.attname] = data

        return data
