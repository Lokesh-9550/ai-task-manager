from django.urls import path
from . import views

urlpatterns = [
    path("", views.task_list, name="task-list"),
    path("tasks/new/", views.task_create, name="task-create"),
    path("tasks/<int:pk>/", views.task_detail, name="task-detail"),
    path("tasks/<int:pk>/edit/", views.task_edit, name="task-edit"),
    path("tasks/<int:pk>/delete/", views.task_delete, name="task-delete"),
    path("tasks/<int:pk>/status/", views.task_update_status, name="task-update-status"),
    path("api/summarize/", views.api_summarize, name="api-summarize"),
    path("projects/", views.project_list, name="project-list"),
    path("projects/new/", views.project_create, name="project-create"),
]
