from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Researcher

class ResearcherSignUpForm(UserCreationForm):
    # Add the extra fields that belong to the Researcher model
    department = forms.CharField(max_length=100, required=True, help_text="E.g., Faculty of Computing")
    research_interests = forms.CharField(widget=forms.Textarea, required=True, help_text="E.g., AI, Data Science")

    class Meta(UserCreationForm.Meta):
        model = User
        # These are the fields from the User model we want to show
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        # 1. Save the base User (username, password, email)
        user = super().save(commit=False)
        user.role = 'Researcher'  # Force the role
        
        if commit:
            user.save()
            # 2. Create the linked Researcher profile
            Researcher.objects.create(
                user_ptr=user, # Link back to the user we just created
                username=user.username, # Required by inheritance
                password=user.password, # Required by inheritance
                department=self.cleaned_data['department'],
                researchinterests=self.cleaned_data['research_interests']
            )
        return user