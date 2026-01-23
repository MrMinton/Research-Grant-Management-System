from django import forms
from .models import Proposal, ProgressReport, Evaluation

class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        # Added 'requested_amount'
        fields = ['title', 'requested_amount', 'pdf_file'] 
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project title...'}),
            
            # STYLING: Border removed to blend with the "RM" input group in HTML
            'requested_amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '0.00',
                'style': 'border: none; box-shadow: none; height: 100%; width: 100%;' 
            }),
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

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['score', 'feedbackComments']
        widgets = {
            'score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'feedbackComments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }