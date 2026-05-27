import json
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from projects.forms import ProjectForm
from projects.models import Project, Skill
from users.views import paginate

SKILLS_AUTOCOMPLETE_LIMIT = 10


def get_project_or_404_json(pk: int):
    project = Project.objects.filter(pk=pk).first()
    if project is None:
        return None, JsonResponse(
            {"status": "error", "detail": "Проект не найден"},
            status=HTTPStatus.NOT_FOUND,
        )
    return project, None


def get_skill_or_404_json(pk: int):
    skill = Skill.objects.filter(pk=pk).first()
    if skill is None:
        return None, JsonResponse(
            {"status": "error", "detail": "Навык не найден"},
            status=HTTPStatus.NOT_FOUND,
        )
    return skill, None


class ProjectListView(View):
    template_name = "projects/project_list.html"

    def get(self, request):
        projects_qs = (
            Project.objects.select_related("owner")
            .prefetch_related("participants", "skills")
            .order_by("-created_at")
        )

        active_skill = request.GET.get("skill", "").strip()
        if active_skill:
            projects_qs = projects_qs.filter(skills__name=active_skill)

        all_skills = Skill.objects.values_list("name", flat=True).order_by("name")

        page_obj, query_prefix = paginate(request, projects_qs, settings.PAGINATE_BY)

        context = {
            "projects": projects_qs,
            "page_obj": page_obj,
            "all_skills": all_skills,
            "active_skill": active_skill,
            "query_prefix": query_prefix,
        }
        return render(request, self.template_name, context)


class ProjectDetailView(View):
    template_name = "projects/project-details.html"

    def get(self, request, pk):
        project = get_object_or_404(
            Project.objects.select_related("owner").prefetch_related(
                "participants", "skills"
            ),
            pk=pk,
        )
        return render(request, self.template_name, {"project": project})


class ProjectCreateView(LoginRequiredMixin, View):
    template_name = "projects/create-project.html"

    def get(self, request):
        form = ProjectForm()
        return render(request, self.template_name, {"form": form, "is_edit": False})

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            return redirect("projects:detail", pk=project.pk)
        return render(request, self.template_name, {"form": form, "is_edit": False})


class ProjectEditView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = "projects/create-project.html"

    def get_project(self, pk):
        return get_object_or_404(Project, pk=pk)

    def test_func(self):
        project = self.get_project(self.kwargs["pk"])
        return self.request.user == project.owner

    def get(self, request, pk):
        project = self.get_project(pk)
        form = ProjectForm(instance=project)
        return render(
            request,
            self.template_name,
            {"form": form, "is_edit": True, "project": project},
        )

    def post(self, request, pk):
        project = self.get_project(pk)
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:detail", pk=project.pk)
        return render(
            request,
            self.template_name,
            {"form": form, "is_edit": True, "project": project},
        )


class ProjectCompleteView(LoginRequiredMixin, View):

    def post(self, request, pk):
        project, error = get_project_or_404_json(pk)
        if error:
            return error

        if request.user != project.owner:
            return JsonResponse(
                {"status": "error", "detail": "Нет прав"},
                status=HTTPStatus.FORBIDDEN,
            )
        if project.status != Project.STATUS_OPEN:
            return JsonResponse(
                {"status": "error", "detail": "Проект уже закрыт"},
                status=HTTPStatus.BAD_REQUEST,
            )
        project.status = Project.STATUS_CLOSED
        project.save(update_fields=["status"])
        return JsonResponse({"status": "ok", "project_status": "closed"})


class ProjectToggleParticipateView(LoginRequiredMixin, View):

    def post(self, request, pk):
        project, error = get_project_or_404_json(pk)
        if error:
            return error

        user = request.user
        if user == project.owner:
            return JsonResponse(
                {"status": "error", "detail": "Автор не может быть участником"},
                status=HTTPStatus.BAD_REQUEST,
            )

        is_participant = project.participants.filter(id=user.id).exists()
        if is_participant:
            project.participants.remove(user)
        else:
            project.participants.add(user)

        return JsonResponse({"status": "ok", "participant": not is_participant})


class SkillAutocompleteView(View):

    def get(self, request):
        query = request.GET.get("q", "").strip()
        skills = Skill.objects.filter(name__istartswith=query).order_by("name")[
            :SKILLS_AUTOCOMPLETE_LIMIT
        ]
        data = [{"id": skill.id, "name": skill.name} for skill in skills]
        return JsonResponse(data, safe=False)


class ProjectSkillAddView(LoginRequiredMixin, View):

    def post(self, request, pk):
        project, error = get_project_or_404_json(pk)
        if error:
            return error

        if request.user != project.owner:
            return JsonResponse(
                {"status": "error", "detail": "Нет прав"},
                status=HTTPStatus.FORBIDDEN,
            )

        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse(
                {"status": "error", "detail": "Неверный JSON"},
                status=HTTPStatus.BAD_REQUEST,
            )

        skill_id = body.get("skill_id")
        name = body.get("name", "").strip()
        created = False
        added = False

        if skill_id:
            skill, error = get_skill_or_404_json(skill_id)
            if error:
                return error
        elif name:
            skill, created = Skill.objects.get_or_create(name=name)
        else:
            return JsonResponse(
                {"status": "error", "detail": "Нужен skill_id или name"},
                status=HTTPStatus.BAD_REQUEST,
            )

        if not project.skills.filter(id=skill.id).exists():
            project.skills.add(skill)
            added = True

        return JsonResponse(
            {
                "skill_id": skill.id,
                "id": skill.id,
                "name": skill.name,
                "created": created,
                "added": added,
            }
        )


class ProjectSkillRemoveView(LoginRequiredMixin, View):

    def post(self, request, pk, skill_pk):
        project, error = get_project_or_404_json(pk)
        if error:
            return error

        if request.user != project.owner:
            return JsonResponse(
                {"status": "error", "detail": "Нет прав"},
                status=HTTPStatus.FORBIDDEN,
            )

        skill, error = get_skill_or_404_json(skill_pk)
        if error:
            return error

        project.skills.remove(skill)
        return JsonResponse({"status": "ok"})
