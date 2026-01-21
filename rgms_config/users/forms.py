from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Researcher

class ResearcherSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Researcher
        fields = UserCreationForm.Meta.fields + ('email', 'department', 'researchinterests')
        
        # FIX: Manually set the UI labels to fix "Researchinterests" typo
        labels = {
            'researchinterests': 'Research Interests',
            'department': 'Department/Faculty',
            'email': 'Email Address'
        }
        
        # OPTIONAL: Add better placeholder text
        widgets = {
            'researchinterests': forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g., AI, Data Science, Cybersecurity'}),
            'department': forms.TextInput(attrs={'placeholder': 'e.g., Faculty of Computing'})
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'Researcher'
        if commit:
            user.save()
        return user