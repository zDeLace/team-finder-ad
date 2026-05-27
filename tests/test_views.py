import pytest
from projects.models import Project

pytestmark = pytest.mark.django_db


def test_project_list_anonymous(client):
    resp = client.get("/projects/list/")
    assert resp.status_code == 200


def test_project_list_with_skill_filter(client, project, skill):
    project.skills.add(skill)
    resp = client.get(f"/projects/list/?skill={skill.name}")
    assert resp.status_code == 200
    assert project.name.encode() in resp.content


def test_project_detail(client, project):
    resp = client.get(f"/projects/{project.id}/")
    assert resp.status_code == 200
    assert project.name.encode() in resp.content


def test_create_project_requires_login(client):
    resp = client.get("/projects/create-project/")
    assert resp.status_code == 302
    assert "/login/" in resp["Location"]


def test_create_project_logged_in(client, user):
    client.force_login(user)
    resp = client.post("/projects/create-project/", {
        "name": "Новый проект",
        "description": "Описание",
        "status": "open",
        "github_url": ""
    })
    assert resp.status_code == 302
    assert Project.objects.filter(name="Новый проект").exists()


def test_complete_project(client, user, project):
    client.force_login(user)
    resp = client.post(
        f"/projects/{project.id}/complete/", content_type="application/json"
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    project.refresh_from_db()
    assert project.status == "closed"


def test_complete_project_not_owner(client, user2, project):
    client.force_login(user2)
    resp = client.post(
        f"/projects/{project.id}/complete/", content_type="application/json"
        )
    assert resp.status_code == 403


def test_toggle_participate(client, user2, project):
    client.force_login(user2)
    resp = client.post(
        f"/projects/{project.id}/toggle-participate/",
        content_type="application/json"
        )
    assert resp.status_code == 200
    assert resp.json()["participant"] is True
    resp2 = client.post(
        f"/projects/{project.id}/toggle-participate/",
        content_type="application/json"
        )
    assert resp2.json()["participant"] is False


def test_skill_autocomplete(client, skill):
    resp = client.get("/projects/skills/?q=Py")
    assert resp.status_code == 200
    data = resp.json()
    assert any(s["name"] == "Python" for s in data)


def test_skill_add(client, user, project, skill):
    client.force_login(user)
    resp = client.post(
        f"/projects/{project.id}/skills/add/",
        data='{"skill_id": ' + str(skill.id) + '}',
        content_type="application/json"
    )
    assert resp.status_code == 200
    assert skill in project.skills.all()


def test_user_list(client):
    resp = client.get("/users/list/")
    assert resp.status_code == 200


def test_register(client):
    resp = client.post("/users/register/", {
        "name": "Новый", "surname": "Пользователь",
        "email": "new@example.com", "password": "securepass"
    })
    assert resp.status_code == 302


def test_login(client, user):
    resp = client.post("/users/login/",
                       {"username": user.email, "password": "pass123"}
                       )
    assert resp.status_code == 302
