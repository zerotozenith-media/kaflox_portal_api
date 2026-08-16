from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.SUPER_ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    # Roles
    SUPER_ADMIN = 'super_admin'
    TEAM_MEMBER = 'team_member'
    CLIENT = 'client'
    EOI_PROSPECT = 'eoi_prospect'

    ROLE_CHOICES = [
        (SUPER_ADMIN, 'Super Admin'),
        (TEAM_MEMBER, 'Team Member'),
        (CLIENT, 'Client'),
        (EOI_PROSPECT, 'EOI Prospect'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=EOI_PROSPECT)
    country = models.CharField(max_length=100, blank=True)
    preferred_currency = models.CharField(max_length=3, default='NGN')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    azure_oid = models.CharField(max_length=100, blank=True, help_text='Azure AD B2C Object ID')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} ({self.email})'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_super_admin(self):
        return self.role == self.SUPER_ADMIN

    @property
    def is_client(self):
        return self.role == self.CLIENT

    @property
    def is_team_member(self):
        return self.role == self.TEAM_MEMBER

    @property
    def is_eoi_prospect(self):
        return self.role == self.EOI_PROSPECT
