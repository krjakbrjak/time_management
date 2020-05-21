from django.db import models
from django.contrib.auth import get_user_model

from .utils import constants

class Date(models.Model):
    ts = models.DateField(auto_now=False)

    def __str__(self):
        return self.ts.strftime('%b %d %Y')

class RequestType(models.Model):
    rtype = models.TextField(null=False, unique=True, editable=False)

    def __str__(self):
        return self.rtype

class Request(models.Model):
    start = models.IntegerField(default=None, null=True)
    end = models.IntegerField(default=None, null=True)
    ts = models.ForeignKey(Date, on_delete=models.CASCADE)

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    rtype = models.ForeignKey(RequestType, default=1, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}: {self.rtype.rtype}'

class Comment(models.Model):
    comment = models.TextField(null=True, default=None)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)

    def __str__(self):
        if len(self.comment) > 9:
            return f'{self.comment[0:10]}...'
        return self.comment
