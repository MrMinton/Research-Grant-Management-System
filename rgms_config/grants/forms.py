from django import forms
from .models import Proposal

class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        # We only ask for the title. 
        # The 'status' (Draft) and 'version' (1.0) are set automatically by your models.py.
        fields = ['title']
        
        # Optional: Add some styling or custom labels
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your research title here...'}),
        }