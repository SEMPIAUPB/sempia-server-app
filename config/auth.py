from rest_framework import authentication
from rest_framework import exceptions

class WorkerAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header == 'Bearer secret':
            class WorkerUser:
                is_authenticated = True
                role = 'WORKER'
            return (WorkerUser(), None)
        return None
