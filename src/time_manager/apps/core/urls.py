from django.urls import re_path
from .views import Authorisation
from .views import ProfileView
from .views import ImageView
from .views import TimeView
from .views import CommentView

from rest_framework.routers import DefaultRouter

app_name = "core"
router = DefaultRouter()
router.register(r'profiles', ProfileView, basename='profile')
router.register(r'images', ImageView, basename='image')
router.register(r'times', TimeView, basename='time')
router.register(r'comments', CommentView, basename='comment')

urlpatterns = [
    re_path(r'^login/$', Authorisation.as_view(), name='authorisation'),
]

urlpatterns += router.urls
