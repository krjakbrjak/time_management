from django.http import JsonResponse
from django.http import HttpResponse

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authentication import authenticate

import base64

from .serializers import UserLoginSerializer
from .serializers import UserLogoutSerializer
from .serializers import ProfileSerializer
from .serializers import ImageSerializer
from .models import Profile
from .models import Image
from .models import ImageMimeType

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
