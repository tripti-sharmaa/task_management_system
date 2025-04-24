from rest_framework import serializers
from .models import User
from .models import Project
from .models import Task
from .models import Comment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'is_active', 'is_admin']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'name', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.
    Handles validation and serialization for project data.
    """
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'manager', 'members']
        read_only_fields = ['id']

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model.
    Handles validation and serialization for task data.
    """
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'project', 'assigned_to', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model.
    Handles validation and serialization for comment data.
    """
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'task', 'project', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Ensure that a comment is associated with either a task or a project.
        """
        if not data.get('task') and not data.get('project'):
            raise serializers.ValidationError("A comment must be associated with either a task or a project.")
        return data