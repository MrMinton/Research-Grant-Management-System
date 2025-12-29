from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import ResearcherSignUpForm
from django.contrib.auth.decorators import login_required

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

@login_required
def dashboard_dispatch(request):
    # --- DEBUGGING START ---
    print(f"LOGGED IN USER: {request.user.username}")
    print(f"USER ROLE: '{request.user.role}'")
    # --- DEBUGGING END ---

    if request.user.role == 'Reviewer':
        return redirect('reviewer_dashboard')
        
    elif request.user.role == 'Researcher':
        return redirect('researcher_dashboard')
        
    # If the role is empty or wrong, it falls through to here:
    return redirect('home')