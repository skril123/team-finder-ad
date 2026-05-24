import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import ProjectForm
from .models import Project, Skill


def project_list(request):
    active_skill = request.GET.get("skill", "").strip()
    projects = (
        Project.objects.select_related("owner")
        .prefetch_related("participants", "skills")
        .order_by("-created_at")
    )
    if active_skill:
        projects = projects.filter(skills__name__iexact=active_skill).distinct()

    paginator = Paginator(projects, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    all_skills = Skill.objects.values_list("name", flat=True).order_by("name")
    context = {
        "projects": page_obj,
        "page_obj": page_obj,
        "all_skills": all_skills,
        "active_skill": active_skill,
    }
    return render(request, "projects/project_list.html", context)


def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants", "skills"),
        pk=pk,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id:
        return HttpResponseForbidden("Редактировать проект может только автор.")

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def complete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id:
        return JsonResponse({"status": "error", "error": "forbidden"}, status=403)
    if project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error", "error": "already_closed"}, status=400)

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": project.status})


@login_required
@require_POST
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": "ok", "participant": participant})


@require_GET
def skills_autocomplete(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.all()
    if query:
        skills = skills.filter(name__istartswith=query)
    data = list(skills.order_by("name").values("id", "name")[:10])
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_project_skill(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id:
        return JsonResponse({"status": "error", "error": "forbidden"}, status=403)

    payload = _request_payload(request)
    skill_id = payload.get("skill_id")
    name = (payload.get("name") or "").strip()

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
        created = False
    elif name:
        skill = Skill.objects.filter(name__iexact=name).first()
        if skill:
            created = False
        else:
            skill = Skill.objects.create(name=name)
            created = True
    else:
        return JsonResponse({"status": "error", "error": "empty_skill"}, status=400)

    added = not project.skills.filter(pk=skill.pk).exists()
    if added:
        project.skills.add(skill)

    return JsonResponse(
        {
            "status": "ok",
            "id": skill.pk,
            "name": skill.name,
            "skill_id": skill.pk,
            "created": created,
            "added": added,
        }
    )


@login_required
@require_POST
def remove_project_skill(request, pk, skill_id):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id:
        return JsonResponse({"status": "error", "error": "forbidden"}, status=403)

    skill = get_object_or_404(Skill, pk=skill_id)
    if not project.skills.filter(pk=skill.pk).exists():
        return JsonResponse({"status": "error", "error": "not_attached"}, status=400)

    project.skills.remove(skill)
    return JsonResponse({"status": "ok", "removed": True})


def _request_payload(request):
    if request.content_type == "application/json" and request.body:
        try:
            return json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return {}
    return request.POST
