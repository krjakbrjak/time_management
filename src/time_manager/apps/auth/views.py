from django.http import JsonResponse
from django.conf import settings

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from .serializers import UserLoginSerializer
from .authentication import ExtendedTokenAuthentication

from . import IsLoggedIn
from .authentication import authenticate

class Authorisation(APIView):
    permission_classes = [IsLoggedIn]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid():
            username = serializer.data['username']
            password = serializer.data['password']
            token = authenticate(username, password)
            if token is not None:
                response = JsonResponse({
                    'user': username
                })
                response.set_cookie(settings.TOKEN_SESSION_COOKIE_NAME or ExtendedTokenAuthentication.keyword, token.key, httponly=True)
                return response

            return JsonResponse({
                "error": 'Wrong credentials!'
            })

        return JsonResponse({"error": serializer.errors})

    def delete(self, request, *args, **kwargs):
        try:
            Token.objects.get(key=request.auth, user=request.user).delete()
        except:
            return JsonResponse({"error": "no user is logged in"})

        return JsonResponse({
            'detail': 'User is logged out',
            'user': request.user.username
        })
