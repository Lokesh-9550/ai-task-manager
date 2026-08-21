import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Task, Project
from .forms import TaskForm, ProjectForm
from .ai_summarizer import summarize_notes


def task_list(request):
    tasks = Task.objects.select_related("project").prefetch_related("assignees").all()

    status = request.GET.get("status")
    project_id = request.GET.get("project")
    if status:
        tasks = tasks.filter(status=status)
    if project_id:
        tasks = tasks.filter(project_id=project_id)

    context = {
        "tasks": tasks,
        "projects": Project.objects.all(),
        "status_choices": Task.STATUS_CHOICES,
        "active_status": status or "",
        "active_project": int(project_id) if project_id else None,
    }
    return render(request, "tasks/task_list.html", context)


def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, "tasks/task_detail.html", {"task": task})


def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            if task.meeting_notes:
                task.ai_summary = summarize_notes(task.meeting_notes)
                task.save(update_fields=["ai_summary"])
            return redirect("task-detail", pk=task.pk)
    else:
        form = TaskForm()
    return render(request, "tasks/task_form.html", {"form": form, "mode": "Create"})


def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            if task.meeting_notes:
                task.ai_summary = summarize_notes(task.meeting_notes)
                task.save(update_fields=["ai_summary"])
            return redirect("task-detail", pk=task.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, "tasks/task_form.html", {"form": form, "mode": "Edit", "task": task})


@require_POST
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return redirect("task-list")


@require_POST
def task_update_status(request, pk):
    """AJAX endpoint used by the board view to drag tasks between columns."""
    task = get_object_or_404(Task, pk=pk)
    data = json.loads(request.body or "{}")
    new_status = data.get("status")
    if new_status not in dict(Task.STATUS_CHOICES):
        return JsonResponse({"error": "invalid status"}, status=400)
    task.status = new_status
    task.save(update_fields=["status"])
    return JsonResponse({"ok": True, "status": task.status})


@require_POST
def api_summarize(request):
    """Standalone endpoint: summarize arbitrary meeting notes without saving a task."""
    data = json.loads(request.body or "{}")
    notes = data.get("notes", "")
    if not notes.strip():
        return JsonResponse({"error": "notes is required"}, status=400)
    summary = summarize_notes(notes)
    return JsonResponse({"summary": summary})


def project_list(request):
    projects = Project.objects.all()
    return render(request, "tasks/project_list.html", {"projects": projects})


def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("project-list")
    else:
        form = ProjectForm()
    return render(request, "tasks/project_form.html", {"form": form})
