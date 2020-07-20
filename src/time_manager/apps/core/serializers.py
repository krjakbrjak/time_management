from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import serializers

import base64

from .models import Profile
from .models import Image
from .models import ImageMimeType
from .models import TimeRequest
from .models import Comment
from .utils import types

class DynamicFieldsMixin():
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        # Because of the rules for constructing MRO, this mixin has
        # to be inherited first. A call to super will take the next
        # element from the root's MRO
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

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

class UserLogoutSerializer(serializers.Serializer):
    ''' A simple serializer to check logout data.
    '''
    username = serializers.CharField()
    token = serializers.CharField()

class UserSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = '__all__'

    def update(self, instance, validated_data):
        ''' Method to update user data.
        It needs to be overidden because raw passwords
        are not stored in the database. For that there
        is a special function that will apply some transformation
        to the password and store the result in the database.
        '''

        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        instance.__dict__.update(validated_data)
        instance.save()

        return instance

class ImageField(serializers.Field):
    ''' Custom field representing image
    '''

    def to_representation(self, instance):
        url = reverse("core:image-detail", kwargs={'pk': instance.pk})
        request = self.context.get('request', None)

        if request is not None:
            return request.build_absolute_uri(url)

        return url

    def to_internal_value(self, a):
        return types.Image(mime_type=a.content_type, blob=base64.b64encode(a.file.read()))

def image_mime_type_validator(a):
    ''' Checks if the data is a of image type
    '''

    if not a.is_valid():
        raise serializers.ValidationError('Only image types are supported')

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    avatar = ImageField(required=False, validators=[image_mime_type_validator])

    def __init__(self, *args, **kwargs):
        user_fields = kwargs.pop('user_fields', None)
        super().__init__(*args, **kwargs)

        if user_fields:
            self.user = UserSerializer(**{"fields": user_fields})

    def create(self, validated_data):
        ''' This function accepts only user data (password/username).
        Profile specific data (avatar/erc.) should be provided in a
        separate update request (PATCH).
        '''

        user = get_user_model().objects.create_user(**validated_data['user'])
        return Profile.objects.create(user=user)

    def update(self, instance, validated_data):
        ''' Updates profile data
        '''

        avatar = validated_data.pop('avatar', None)
        if avatar:
            mime_type = ImageMimeType.objects.get(name=avatar.mime_type)
            instance.avatar = Image(mime_type=mime_type, blob=avatar.blob)
            instance.avatar.save()

        user = validated_data.pop('user', None)
        if user:
            instance.user = UserSerializer().update(instance.user, user)

        instance.save()

        return instance

    class Meta:
        model = Profile
        fields = '__all__'

class ImageMimeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageMimeType
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class TimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeRequest
        fields = '__all__'

class TimeReadSerializer(serializers.ModelSerializer):
    ''' Convenience serializer returning a link to user
    instead of the actual data
    '''

    user = serializers.HyperlinkedRelatedField(view_name='core:profile-detail', read_only=True)

    class Meta:
        model = TimeRequest
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    ''' Comment serializer
    '''

    class Meta:
        model = Comment
        fields = '__all__'
