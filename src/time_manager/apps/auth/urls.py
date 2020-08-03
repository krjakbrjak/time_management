from django.urls import re_path
from .views import Authorisation

app_name = "auth"

urlpatterns = [
    re_path(r'^login/$', Authorisation.as_view(), name='login'),
]
