from django import forms
from .models import Task, Project


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "project", "title", "description", "assignees",
            "status", "priority", "due_date", "meeting_notes",
        ]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "meeting_notes": forms.Textarea(attrs={"rows": 5, "placeholder": "Paste raw meeting notes here to auto-generate a summary + action items..."}),
            "assignees": forms.CheckboxSelectMultiple(),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "members"]
        widgets = {
            "members": forms.CheckboxSelectMultiple(),
        }
