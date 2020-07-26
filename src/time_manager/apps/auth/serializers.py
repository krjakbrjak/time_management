from rest_framework import serializers

class UserLoginSerializer(serializers.Serializer):
    ''' A simple serializer to check login
    data. ModelSerializer cannot be used here
    since that will involve all constraints installed for
    the fields. For example, username is required to be unique
    (see User model definition), but that will fail validation
    of data posted for login information (user already exists).
    '''
    username = serializers.CharField()
    password = serializers.CharField()
