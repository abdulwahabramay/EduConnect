from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import CustomToken

class ExpiringTokenAuthentication(TokenAuthentication):
    model = CustomToken

    def authenticate(self, request):
        auth = super().authenticate(request)
        if auth is None:
            return None
        user, token = auth
        if token.is_expired():
            token.delete()  # Delete the expired token
            raise AuthenticationFailed('Token has expired.')
        return (user, token)