from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    description = forms.CharField(
        # this mix business logic with view (templates),
        # but there is no easy way to avoid it.
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Task Name...',
            'aria-label':"Task name",
            'aria-describedby':"button-addon2"
        }),
        label=u'',
        required=True
    )
    priority = forms.ChoiceField(
        # this mix business logic with view (templates),
        # but there is no easy way to avoid it.
        choices=Task.PRIORITIES,
        label=u'Medium',
        required=True,
        widget=forms.Select(attrs={
            'type': 'dropdown-menu',
            'class': 'form-control',
            #'placeholder': 'Task Name...',
            #'aria-label':"Task name",
            #'aria-describedby':"button-addon2"
        }),
    )
    class Meta:
        model = Task
        fields = ('description', 'priority') # priority

class StatusTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('status',)