from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    acc: str = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Идентификатор Efics",
        help_text="Идентификатор аккаунта из приложения Efics (необязательно)"
    )

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        verbose_name='Группы',
        help_text='Группы, к которым принадлежит пользователь'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True,
        verbose_name='Разрешения',
        help_text='Разрешения, выданные пользователю'
    )