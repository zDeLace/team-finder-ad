import pytest
from django.contrib.auth import get_user_model
from projects.models import Project, Skill

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@example.com", name="Тест", surname="Тестов", password="pass123"
    )


@pytest.fixture
def user2(db):
    return User.objects.create_user(
        email="test2@example.com", name="Другой", surname="Юзер", password="pass123"
    )


@pytest.fixture
def project(db, user):
    return Project.objects.create(name="Тестовый проект", owner=user, status="open")


@pytest.fixture
def skill(db):
    return Skill.objects.create(name="Python")
