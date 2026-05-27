from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from core.constants import SKILLS_AUTOCOMPLETE_LIMIT
from core.services import get_request_payload, paginate_queryset
from projects.forms import ProjectForm
from projects.models import Project, Skill


def project_list(request):
    active_skill = request.GET.get("skill", "").strip()
    projects = Project.objects.select_related("owner").prefetch_related("participants", "skills")
    if active_skill:
        projects = projects.filter(skills__name__iexact=active_skill).distinct()

    page_obj = paginate_queryset(request, projects)
    all_skills = Skill.objects.values_list("name", flat=True)
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
    form = ProjectForm(data=request.POST if request.method == "POST" else None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:detail", pk=project.pk)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id:
        return HttpResponseForbidden("Редактировать проект может только автор.")

    form = ProjectForm(data=request.POST if request.method == "POST" else None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:detail", pk=project.pk)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def complete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id:
        return JsonResponse({"status": "error", "error": "forbidden"}, status=HTTPStatus.FORBIDDEN)
    if project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error", "error": "already_closed"}, status=HTTPStatus.BAD_REQUEST)

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": project.status})


@login_required
@require_POST
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    is_participant = project.participants.filter(pk=request.user.pk).exists()
    if is_participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)
    participant = not is_participant
    return JsonResponse({"status": "ok", "participant": participant})


@require_GET
def skills_autocomplete(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.all()
    if query:
        skills = skills.filter(name__istartswith=query)
    data = list(skills.values("id", "name")[:SKILLS_AUTOCOMPLETE_LIMIT])
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_project_skill(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id:
        return JsonResponse({"status": "error", "error": "forbidden"}, status=HTTPStatus.FORBIDDEN)

    payload = get_request_payload(request)
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
        return JsonResponse({"status": "error", "error": "empty_skill"}, status=HTTPStatus.BAD_REQUEST)

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
        return JsonResponse({"status": "error", "error": "forbidden"}, status=HTTPStatus.FORBIDDEN)

    skill = get_object_or_404(Skill, pk=skill_id)
    if not project.skills.filter(pk=skill.pk).exists():
        return JsonResponse({"status": "error", "error": "not_attached"}, status=HTTPStatus.BAD_REQUEST)

    project.skills.remove(skill)
    return JsonResponse({"status": "ok", "removed": True})
