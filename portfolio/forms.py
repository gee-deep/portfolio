from django import forms
from .models import LifeEvent

class LifeEventForm(forms.ModelForm):
    class Meta:
        model = LifeEvent
        fields = ['title', 'description', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'markdown-editor'})
        } 