from django.urls import path

from projects import views

app_name = "projects"

urlpatterns = [
    path("list/", views.ProjectListView.as_view(), name="list"),
    path("skills/", views.SkillAutocompleteView.as_view(), name="skills_autocomplete"),
    path("create-project/", views.ProjectCreateView.as_view(), name="create"),
    path("<int:pk>/", views.ProjectDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.ProjectEditView.as_view(), name="edit"),
    path("<int:pk>/complete/", views.ProjectCompleteView.as_view(), name="complete"),
    path(
        "<int:pk>/toggle-participate/",
        views.ProjectToggleParticipateView.as_view(),
        name="toggle_participate",
    ),
    path("<int:pk>/skills/add/", views.ProjectSkillAddView.as_view(), name="skill_add"),
    path(
        "<int:pk>/skills/<int:skill_pk>/remove/",
        views.ProjectSkillRemoveView.as_view(),
        name="skill_remove",
    ),
]
