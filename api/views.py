from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserSerializer, SignupSerializer, LoginSerializer, ProjectSerializer, TaskSerializer, CommentSerializer
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import User, Project, Task, Comment
from .permissions import IsAdminUser  # Custom permission class
import logging

logger = logging.getLogger(__name__)

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


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing projects.
    Provides CRUD operations for projects with role-based access control.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """
        Restrict the queryset based on the user's role.
        Admins can see all projects, while other roles see only their projects.
        """
        user = self.request.user
        if user.role == 'Admin':
            return Project.objects.all()
        return Project.objects.filter(members=user)

    def perform_create(self, serializer):
        """
        Automatically set the manager to the logged-in user when creating a project.
        """
        serializer.save(manager=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Allow only the project manager or admin to update the project.
        """
        project = self.get_object()
        if request.user != project.manager and request.user.role != 'Admin':
            return Response({'error': 'You do not have permission to update this project.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Allow only the project manager or admin to delete the project.
        """
        project = self.get_object()
        if request.user != project.manager and request.user.role != 'Admin':
            return Response({'error': 'You do not have permission to delete this project.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks.
    Provides CRUD operations for tasks with role-based access control.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        """
        Restrict the queryset based on the user's role.
        Admins and project managers can see all tasks, while other roles see only their assigned tasks.
        """
        user = self.request.user
        if user.role in ['Admin', 'Project Manager']:
            return Task.objects.all()
        return Task.objects.filter(assigned_to=user)

    def perform_create(self, serializer):
        """
        Automatically set the creator as the assigned user if not provided.
        """
        serializer.save()

    def update(self, request, *args, **kwargs):
        """
        Allow only the task assignee, project manager, or admin to update the task.
        """
        task = self.get_object()
        if request.user != task.assigned_to and request.user.role not in ['Admin', 'Project Manager']:
            return Response({'error': 'You do not have permission to update this task.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Allow only the task assignee, project manager, or admin to delete the task.
        """
        task = self.get_object()
        if request.user != task.assigned_to and request.user.role not in ['Admin', 'Project Manager']:
            return Response({'error': 'You do not have permission to delete this task.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments.
    Provides CRUD operations for comments with role-based access control.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        """
        Restrict the queryset based on the user's role.
        Admins and project managers can see all comments, while other roles see only their own comments.
        """
        user = self.request.user
        if user.role in ['Admin', 'Project Manager']:
            return Comment.objects.all()
        return Comment.objects.filter(author=user)

    def perform_create(self, serializer):
        """
        Automatically set the author to the logged-in user when creating a comment.
        Ensure that either a task or a project is provided.
        Log the data being sent for debugging purposes.
        """
        logger.debug(f"Comment creation data: {serializer.validated_data}")
        if not serializer.validated_data.get('task') and not serializer.validated_data.get('project'):
            raise serializer.ValidationError("A comment must be associated with either a task or a project.")
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Allow only the comment author or admin to update the comment.
        """
        comment = self.get_object()
        if request.user != comment.author and request.user.role != 'Admin':
            return Response({'error': 'You do not have permission to update this comment.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Allow only the comment author or admin to delete the comment.
        """
        comment = self.get_object()
        if request.user != comment.author and request.user.role != 'Admin':
            return Response({'error': 'You do not have permission to delete this comment.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
