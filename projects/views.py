import json

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.conf import settings

from projects.forms import ProjectForm
from projects.models import Project, Skill


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

        paginator = Paginator(projects_qs, settings.PAGINATE_BY)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        query_params = request.GET.copy()
        query_params.pop("page", None)
        query_prefix = query_params.urlencode()
        if query_prefix:
            query_prefix += "&"

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
        project = get_object_or_404(Project, pk=pk)
        if request.user != project.owner:
            return JsonResponse({"status": "error", "detail": "Нет прав"}, status=403)
        if project.status != Project.STATUS_OPEN:
            return JsonResponse(
                {"status": "error", "detail": "Проект уже закрыт"}, status=400
            )
        project.status = Project.STATUS_CLOSED
        project.save(update_fields=["status"])
        return JsonResponse({"status": "ok", "project_status": "closed"})


class ProjectToggleParticipateView(LoginRequiredMixin, View):

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        user = request.user

        if user == project.owner:
            return JsonResponse(
                {"status": "error", "detail": "Автор не может быть участником"},
                status=400,
            )

        if user in project.participants.all():
            project.participants.remove(user)
            participant = False
        else:
            project.participants.add(user)
            participant = True

        return JsonResponse({"status": "ok", "participant": participant})


class SkillAutocompleteView(View):

    def get(self, request):
        q = request.GET.get("q", "").strip()
        skills = Skill.objects.filter(name__istartswith=q).order_by("name")[:10]
        data = [{"id": s.id, "name": s.name} for s in skills]
        return JsonResponse(data, safe=False)


class ProjectSkillAddView(LoginRequiredMixin, View):

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if request.user != project.owner:
            return JsonResponse({"status": "error", "detail": "Нет прав"}, status=403)

        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse(
                {"status": "error", "detail": "Неверный JSON"}, status=400
            )

        skill_id = body.get("skill_id")
        name = body.get("name", "").strip()

        created = False
        added = False

        if skill_id:
            skill = get_object_or_404(Skill, pk=skill_id)
        elif name:
            skill, created = Skill.objects.get_or_create(name=name)
        else:
            return JsonResponse(
                {"status": "error", "detail": "Нужен skill_id или name"}, status=400
            )

        if skill not in project.skills.all():
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
        project = get_object_or_404(Project, pk=pk)
        if request.user != project.owner:
            return JsonResponse({"status": "error", "detail": "Нет прав"}, status=403)

        skill = get_object_or_404(Skill, pk=skill_pk)
        project.skills.remove(skill)
        return JsonResponse({"status": "ok"})
