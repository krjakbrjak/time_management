from django.http import JsonResponse
from django.http import HttpResponse

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token
from rest_framework.authentication import authenticate
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
from .models import Profile
from .models import Image
from .models import ImageMimeType
from .models import TimeRequest
from .models import RequestType

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

class IsLoggedIn(permissions.IsAuthenticated):
    ''' Allows unauthorized POST calls (login).
    Requires authorization for DELETE (logout).
    '''
    def has_permission(self, request, view):
        if request.method in ['DELETE']:
            return super().has_permission(request, view)

        return True

class Authorisation(APIView):
    permission_classes = [IsLoggedIn]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid():
            username = serializer.data['username']
            password = serializer.data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                token, _ = Token.objects.get_or_create(user=user)
                return JsonResponse({
                    'token': token.key,
                    'user': username
                })

            return JsonResponse({
                "error": 'Wrong credentials!'
            })

        return JsonResponse({"error": serializer.errors})

    def delete(self, request, *args, **kwargs):
        data = request.data
        serializer = UserLogoutSerializer(data=data)

        if serializer.is_valid():
            username = serializer.data['username']
            token = serializer.data['token']
            Token.objects.get(user__username=username, key=token).delete()
            return JsonResponse({
                'detail': 'User is logged out',
                'user': username
            })

        return JsonResponse({"error": serializer.errors})

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

    def initial(self, request, *args, **kwargs):
        ''' Add user to request's data
        '''

        super().initial(request, *args, **kwargs)

        # User is added to request's data only inside POST method,
        # i.e. when the instance is created
        if request.method in ['POST']:
            try:
                profile = Profile.objects.get(user=request.user)
                request.data['user'] = profile.id
            except Profile.DoesNotExist:
                # If this happens then user and profile are not in sync
                raise InternalServerError()

        return request

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
