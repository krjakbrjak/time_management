from rest_framework import permissions

default_app_config = 'time_manager.apps.auth.apps.AuthConfig'

class IsLoggedIn(permissions.IsAuthenticated):
    ''' Allows unauthorized POST calls (login).
    Requires authorization for DELETE (logout).
    '''
    def has_permission(self, request, view):
        if request.method in ['DELETE']:
            return super().has_permission(request, view)

        return True
