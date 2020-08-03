from django.conf import settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authentication import authenticate as drf_authenticate

class ExtendedTokenAuthentication(TokenAuthentication):
    ''' Extended Token Authentication

    If HTTP Cookie `TOKEN_SESSION_COOKIE_NAME` or `self.keyword` is set then
    it contains the token and authentication will be done against it. Otherwise,
    default drf's TokenAuthentication mechanism will work.
    '''
    def authenticate(self, request):
        keyword = settings.TOKEN_SESSION_COOKIE_NAME or self.keyword
        token = request.COOKIES.get(keyword)
        if token:
            return self.authenticate_credentials(token)

        return super().authenticate(request)

def authenticate(username, password):
    ''' Authenticates user

    Parameters
    username (str): Username
    password (str): Password

    Returns
    None: If credentials are wrong
    Token: User token
    '''
    user = drf_authenticate(username=username, password=password)
    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        return token

    return None
