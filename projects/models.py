from django.db import models
from django.conf import settings

from users.validators import validate_github_url


class Skill(models.Model):
    name = models.CharField(
        max_length=124,
        unique=True,
        verbose_name="Навык",
        db_index=True,
    )

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Project(models.Model):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Открыт"),
        (STATUS_CLOSED, "Закрыт"),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name="Название проекта",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Описание",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор",
        db_index=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
        db_index=True,
    )
    github_url = models.URLField(
        blank=True,
        default="",
        verbose_name="GitHub",
        validators=[validate_github_url],
    )
    status = models.CharField(
        max_length=6,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
        verbose_name="Статус",
        db_index=True,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="Участники",
    )
    skills = models.ManyToManyField(
        Skill,
        related_name="projects",
        blank=True,
        verbose_name="Необходимые навыки",
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["owner"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def is_open(self) -> bool:
        return self.status == self.STATUS_OPEN
