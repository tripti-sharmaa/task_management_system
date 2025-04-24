from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserSerializer, SignupSerializer, LoginSerializer
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import User
from .permissions import IsAdminUser  # Custom permission class

class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]  # Use the custom permission class
    # If you want to customize any of the methods, you can override them here
    def create(self, request):
        # Check if the user is authenticated and has admin privileges before creating a new user
        if not request.user.is_authenticated:
            return Response({'error': 'User is not authenticated. Please log in.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not User.objects.filter(id=request.user.id, role='Admin').exists():
            return Response({'error': 'Sorry, you don\'t have privileges.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not authenticated. Please log in.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not User.objects.filter(id=request.user.id, role='Admin').exists():
            return Response({'error': 'Sorry, you don\'t have privileges.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = self.get_object()
            serializer = self.get_serializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response({'error': 'User is not authenticated. Please log in.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not User.objects.filter(id=request.user.id, role='Admin').exists():
            return Response({'error': 'Sorry, you don\'t have privileges.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = self.get_object()
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class AuthViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]  # Add for token verification
    permission_classes = [AllowAny]

   
    def get_serializer(self, *args, **kwargs):
        if self.action == 'signup':
            return SignupSerializer(*args, **kwargs)
        elif self.action == 'login':
            return LoginSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    refresh = RefreshToken.for_user(user)
                    userA = authenticate(username=email, password=password)
                    if userA is not None:
                        login(request,userA)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'user': {
                            'id': user.id,
                            'email': user.email,
                            'name': user.name,
                            'role': user.role
                        },
                        'message': 'Login successful!'
                    })
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        # Debug the Authorization header
        print("Authorization Header:", request.headers.get('Authorization'))
        # Check if the user is authenticated
        if request.user.is_authenticated:
            return Response({"message": "Welcome Back!"}, status=status.HTTP_200_OK)
        return Response({"message": "Please sign up and log in to continue."}, status=status.HTTP_200_OK)
