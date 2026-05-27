from django.contrib import admin

from projects.models import Project, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "owner", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["name", "owner__email"]
    filter_horizontal = ["participants", "skills"]
    ordering = ["-created_at"]
