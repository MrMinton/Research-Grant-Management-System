from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Proposal
from .forms import ProposalForm

@login_required
def researcher_dashboard(request):
    # Security: Only Researchers should see this
    if request.user.role != 'Researcher':
        return redirect('home') 
    
    # Get the specific researcher profile linked to this user
    researcher_profile = request.user.researcher
    
    # Get only proposals that belong to THIS researcher
    my_proposals = Proposal.objects.filter(researcher=researcher_profile)
    
    return render(request, 'grants/dashboard.html', {'proposals': my_proposals})

@login_required
def submit_proposal(request):
    if request.user.role != 'Researcher':
        return redirect('home')

    if request.method == 'POST':
        form = ProposalForm(request.POST)
        if form.is_valid():
            # Create the object but don't save to DB yet
            proposal = form.save(commit=False)
            # Attach the logged-in researcher
            proposal.researcher = request.user.researcher
            # Now save it
            proposal.save()
            return redirect('researcher_dashboard')
    else:
        form = ProposalForm()
    return render(request, 'grants/submit_proposal.html', {'form': form})