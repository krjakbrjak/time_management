from django.db import models
from django.contrib.auth import get_user_model

from .utils import constants

class ImageMimeType(models.Model):
    name = models.TextField(null=False, unique=True)

class Image(models.Model):
    mime_type = models.ForeignKey(ImageMimeType, null=False, on_delete=models.CASCADE)
    blob = models.BinaryField(editable=True)

class Profile(models.Model):
    '''Extends standard User model with some extra information:
    - User's avatar
    '''

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    avatar = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username

class RequestType(models.Model):
    rtype = models.TextField(null=False, unique=True, editable=False)

    def __str__(self):
        return self.rtype

class TimeRequest(models.Model):
    start = models.DateTimeField(default=None, null=True)
    end = models.DateTimeField(default=None, null=True)

    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    rtype = models.ForeignKey(RequestType, default=1, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}: {self.rtype.rtype}'

class Comment(models.Model):
    comment = models.TextField(null=True, default=None)
    request = models.ForeignKey(TimeRequest, on_delete=models.CASCADE)
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)

    def __str__(self):
        if len(self.comment) > 9:
            return f'{self.comment[0:10]}...'
        return self.comment
