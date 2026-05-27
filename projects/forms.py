from django import forms

from projects.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Название проекта"}),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Опишите ваш проект",
                    "rows": 4,
                }
            ),
            "github_url": forms.URLInput(
                attrs={"placeholder": "https://github.com/username/repo"}
            ),
            "status": forms.Select(choices=Project.STATUS_CHOICES),
        }
        labels = {
            "name": "Название",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
            "status": "Статус",
        }
