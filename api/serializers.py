from rest_framework import serializers
from .models import User

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