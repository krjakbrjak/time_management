from django.http import JsonResponse
from django.http import HttpResponse

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.exceptions import APIException

import base64

from .serializers import UserLoginSerializer
from .serializers import UserLogoutSerializer
from .serializers import ProfileSerializer
from .serializers import ImageSerializer
from .serializers import TimeSerializer
from .serializers import TimeReadSerializer
from .serializers import UserSerializer
from .serializers import CommentSerializer
from .models import Profile
from .models import Image
from .models import ImageMimeType
from .models import TimeRequest
from .models import RequestType
from .models import Comment

class ProfilePermissions(permissions.BasePermission):
    ''' Admin can do any requests,
    Authorized users can only get (GET) information
    or update (PATCH) it.
    '''

    def has_permission(self, request, view):
        if permissions.IsAdminUser().has_permission(request, view):
            return True

        if request.method in ['PATCH', 'GET']:
            return permissions.IsAuthenticated().has_permission(request, view)

        return False

class ProfileView(viewsets.ModelViewSet):
    queryset = Profile.objects.all().select_related()
    serializer_class = ProfileSerializer
    permission_classes = [ProfilePermissions]

class SessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = Profile.objects.get(user__id=request.user.id)
        serializer = ProfileSerializer(profile)
        data = serializer.data
        user = UserSerializer(fields=('username',), data=data['user'], partial=True)
        # Since the serializer was initialized with 'data=' then
        # is_valid method has to be called before accessing the data.
        # But is_valid would return False because there would be at
        # least unique constraint violation on username field.
        # The initial data passed to UserSerializer is valid data,
        # because this data was just generated from the actual profile
        # entry. Thus simply ignoring the return of is_valid and using the data
        # is good (even though it is a workaround that needs be solved in django)
        user.is_valid()
        # Use a cut version of a user, no need to pass passwords, etc.
        data['user'] = user.data
        return JsonResponse({
            'profile': data
        })

class ImageView(viewsets.ViewSet):
    ''' View that is able to process get requests for images (avatars)
    '''

    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        image = Image.objects.get(pk=kwargs['pk'])
        response = HttpResponse(base64.b64decode(image.blob), content_type=image.mime_type.name)
        return response

class InternalServerError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Internl server error'
    default_code = 'internal_server_error'

class AddCurrentUserMixin():
    ''' Mixin that adds current user to a request
    '''

    def create(self, request, *args, **kwargs):
        # Unfortunately there is no easy/good way to change the original
        # request (in this case adding current user to its data), because
        # it is implemented as immutable. Changing private memeber _mutable
        # is not an option, well, because it is private. The easiest
        # approach is reimplement CreateModelMixin's create method => deepcopy
        # original request data (it is immutable) and update its copy with user
        # information.
        data = request.data.copy()
        profile = Profile.objects.get(user=request.user)
        data['user'] = profile.id

        # the rest is original implementation of CreateModelMixin's create method.
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class TimeRequestMixin():
    ''' Implements ModelViewSet's methods
    '''

    def _convert_to_hyperlink(self, request, response):
        ''' Converts response to a request:
        user -> hyperlink to user
        '''

        tr = TimeRequest.objects.get(pk=response.data['id'])
        response.data = TimeReadSerializer(tr, context={
            'request': request
        }).data

        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        return self._convert_to_hyperlink(request, response)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)

        return self._convert_to_hyperlink(request, response)

class TimeView(AddCurrentUserMixin, TimeRequestMixin, viewsets.ModelViewSet):
    queryset = TimeRequest.objects.all().select_related()
    serializer_class = TimeSerializer
    permission_classes = [permissions.IsAuthenticated]

class CommentView(AddCurrentUserMixin, viewsets.ModelViewSet):
    queryset = Comment.objects.all().select_related()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
