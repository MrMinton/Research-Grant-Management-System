from django import forms
from .models import Proposal , Evaluation

class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['title', 'pdf_file'] 
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title...'}),
        }

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['score', 'feedbackComments']
        widgets = {
            'score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'feedbackComments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }