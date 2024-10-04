from rest_framework import viewsets, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from users.models import CustomUser
from users.serializers import UserSerializer
from .serializers import CustomUserRegistrationSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class CustomUserRegistrationView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserRegistrationSerializer
    permission_classes = [AllowAny]  

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  
        return Response({'username': user.username, 'role': user.role}, status=status.HTTP_201_CREATED)

class AuthViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny, IsAuthenticated]  

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'role': user.role}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            request.user.auth_token.delete() 
            return Response({"detail": "Logged out successfully."}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)



from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import CustomUser
from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
import base64
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                
                # Debugging user.pk
                print(f"DEBUG: user.pk = {user.pk}")  # Check if user.pk is valid
                
                # Generate token and properly encode UID
                token = default_token_generator.make_token(user)
                uid = base64.urlsafe_b64encode(force_bytes(str(user.pk))).decode('utf-8')  # Properly encode the user's ID
                
                # Debugging the encoded UID
                print(f"DEBUG: Encoded UID = {uid}")  # Check if UID is encoded correctly

                # Generate reset link
                reset_link = f"http://yourdomain.com/api/password-reset-confirm/?uid={uid}&token={token}"
                send_mail(
                    'Password Reset Request',
                    f'Click the link to reset your password: {reset_link}',
                    'from@example.com',  # Replace with your sender email
                    [email],  # Recipient email
                    fail_silently=False,
                )

                return Response({"message": "Password reset email has been sent."}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            uidb64 = serializer.validated_data['uid']
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']

            try:
                # Decode the UID
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = CustomUser.objects.get(pk=uid)

                # Validate the token
                if not default_token_generator.check_token(user, token):
                    return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

                # Set the new password
                user.set_password(new_password)
                user.save()

                return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
            except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                return Response({"error": "Invalid UID."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)