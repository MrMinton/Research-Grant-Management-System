from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import ResearcherSignUpForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification

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
    if request.user.role == 'Reviewer':
        return redirect('reviewer_dashboard')
    elif request.user.role == 'Researcher':
        return redirect('researcher_dashboard')
    elif request.user.role == 'HOD':
        return redirect('hod_dashboard')
    return redirect('home')

@login_required
@require_POST
def mark_notifications_read(request):
    """Marks all notifications for the user as read."""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})