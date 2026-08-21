from django.contrib import admin
from .models import Task, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    filter_horizontal = ("members",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "priority", "due_date")
    list_filter = ("status", "priority", "project")
    filter_horizontal = ("assignees",)
