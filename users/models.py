from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from users.managers import UserManager
from users.validators import validate_github_url, validate_phone

NAME_MAX_LENGTH = 124
SURNAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
ABOUT_MAX_LENGTH = 256


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        db_index=True,
    )
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name="Имя",
    )
    surname = models.CharField(
        max_length=SURNAME_MAX_LENGTH,
        verbose_name="Фамилия",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        verbose_name="Аватар",
        blank=True,
    )
    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
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
        max_length=ABOUT_MAX_LENGTH,
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

            letter = self.name[0] if self.name else "U"
            avatar_file = generate_avatar(letter)
            self.avatar.save(f"avatar_{self.email}.png", avatar_file, save=False)
        super().save(*args, **kwargs)
