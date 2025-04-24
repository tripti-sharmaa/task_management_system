from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, name=None, role=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not role:
            raise ValueError("Users must have a role")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            role=role
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, name=None):
        user = self.create_user(email, password=password, name=name, role='Admin')
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Project Manager', 'Project Manager'),
        ('Project Lead', 'Project Lead'),
        ('Developer', 'Developer'),
        ('Client', 'Client'),
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, default='Unknown')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_permission_set",
        related_query_name="custom_user_permission",
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin