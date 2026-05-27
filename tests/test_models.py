import pytest
from django.contrib.auth import get_user_model
from projects.models import Skill

User = get_user_model()


@pytest.mark.django_db
def test_user_creation_generates_avatar():
    user = User.objects.create_user(
        email="avatar@test.com", name="Аня", surname="Петрова", password="pass"
    )
    assert user.avatar


@pytest.mark.django_db
def test_user_str(user):
    assert "Тест" in str(user)
    assert "test@example.com" in str(user)


@pytest.mark.django_db
def test_project_str(project):
    assert "Тестовый проект" in str(project)


@pytest.mark.django_db
def test_project_is_open(project):
    assert project.is_open is True
    project.status = "closed"
    project.save()
    assert project.is_open is False


@pytest.mark.django_db
def test_skill_unique():
    Skill.objects.create(name="Django")
    skill, created = Skill.objects.get_or_create(name="Django")
    assert not created


@pytest.mark.django_db
def test_project_participants(project, user2):
    project.participants.add(user2)
    assert user2 in project.participants.all()
    assert project in user2.participated_projects.all()


@pytest.mark.django_db
def test_project_skills(project, skill):
    project.skills.add(skill)
    assert skill in project.skills.all()
    assert project in skill.projects.all()
