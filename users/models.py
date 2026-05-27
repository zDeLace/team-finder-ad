from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
    )
from django.db import models

from users.validators import validate_phone, validate_github_url


class UserManager(BaseUserManager):
    def create_user(
            self,
            email: str,
            name: str,
            surname: str,
            password: str = None,
            **extra_fields
            ):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(
            email=email, name=name, surname=surname, **extra_fields
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self,
            email: str,
            name: str,
            surname: str,
            password: str = None,
            **extra_fields
            ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, name, surname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        db_index=True,
    )
    name = models.CharField(
        max_length=124,
        verbose_name="Имя",
    )
    surname = models.CharField(
        max_length=124,
        verbose_name="Фамилия",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        verbose_name="Аватар",
        blank=True,
    )
    phone = models.CharField(
        max_length=12,
        blank=True,
        default="",
        verbose_name="Телефон",
        validators=[validate_phone],
    )
    github_url = models.URLField(
        blank=True,
        default="",
        verbose_name="GitHub",
        validators=[validate_github_url],
    )
    about = models.TextField(
        blank=True,
        default="",
        max_length=256,
        verbose_name="О себе",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Администратор")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["surname", "name"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} {self.surname} <{self.email}>"

    def get_full_name(self) -> str:
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            from users.utils import generate_avatar
            letter = (self.name[0] if self.name else "U")
            avatar_file = generate_avatar(letter)
            self.avatar.save(
                f"avatar_{self.email}.png", avatar_file, save=False
                )
        super().save(*args, **kwargs)
