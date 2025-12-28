from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import ResearcherSignUpForm


def home(request):
    return render(request, 'home.html')

def register_researcher(request):
    if request.method == 'POST':
        form = ResearcherSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Auto-login the user after signup
            return redirect('researcher_dashboard')
    else:
        form = ResearcherSignUpForm()
    return render(request, 'users/register_researcher.html', {'form': form})