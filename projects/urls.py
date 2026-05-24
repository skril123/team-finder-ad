from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("list/", views.project_list, name="list"),
    path("list", views.project_list),
    path("create-project/", views.create_project, name="create"),
    path("create-project", views.create_project),
    path("skills/", views.skills_autocomplete, name="skills_autocomplete"),
    path("<int:pk>/", views.project_detail, name="detail"),
    path("<int:pk>", views.project_detail),
    path("<int:pk>/edit/", views.edit_project, name="edit"),
    path("<int:pk>/edit", views.edit_project),
    path("<int:pk>/complete/", views.complete_project, name="complete"),
    path("<int:pk>/toggle-participate/", views.toggle_participate, name="toggle_participate"),
    path("<int:pk>/skills/add/", views.add_project_skill, name="add_skill"),
    path("<int:pk>/skills/<int:skill_id>/remove/", views.remove_project_skill, name="remove_skill"),
]
