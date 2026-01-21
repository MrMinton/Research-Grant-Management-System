from django import forms
from .models import Proposal, ProgressReport

class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['title', 'pdf_file'] 
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title...'}),
        }

# --- NEW ADDITION --- by Law
class ProgressReportForm(forms.ModelForm):
    class Meta:
        model = ProgressReport
        fields = ['content', 'milestonesAchieved']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Detailed description of progress...'}),
            'milestonesAchieved': forms.Textarea(attrs={'rows': 3, 'placeholder': 'List key milestones met...'}),
        }