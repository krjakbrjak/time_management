from django.db import models
from django.contrib.auth.models import User

class Date(models.Model):
    ts = models.DateField(auto_now=True)

class Request(models.Model):
    TYPES = (
        (0, "general"),
    )

    start = models.IntegerField(default=None, null=True)
    end = models.IntegerField(default=None, null=True)
    ts = models.ForeignKey(Date, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rtype = models.IntegerField(default=0, null=False, choices=TYPES)

class Comment(models.Model):
    comment = models.TextField(null=True, default=None)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
