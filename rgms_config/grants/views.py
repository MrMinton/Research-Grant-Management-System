from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Proposal, Grant, Budget, Evaluation
from .forms import ProposalForm , EvaluationForm
from decimal import Decimal

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
            proposal = form.save(commit=False)
            proposal.researcher = request.user.researcher
            proposal.save()
            return redirect('researcher_dashboard')
    else:
        form = ProposalForm()
    return render(request, 'grants/submit_proposal.html', {'form': form})

@login_required
def reviewer_dashboard(request):
    # 1. Security check: Ensure the user is actually a Reviewer
    if request.user.role != 'Reviewer':
        return redirect('home')

    # 2. Get proposals. 
    # Reviewers should see everything that is NOT a 'Draft'.
    proposals_to_review = Proposal.objects.exclude(status='Draft')

    context = {
        'proposals': proposals_to_review
    }
    return render(request, 'users/reviewer_dashboard.html', context)


# HOD PART

@login_required
def hod_dashboard(request):
    # Security: Ensure only HODs can access
    if request.user.role != 'HOD':
        return redirect('home')

    proposals = Proposal.objects.filter(status='Review Complete')
    
    # Fetch active grants for the monitoring section
    active_grants = Grant.objects.all()

    return render(request, 'grants/hod_dashboard.html', {
        'proposals': proposals,
        'active_grants': active_grants
    })

@login_required
def approve_proposal(request, proposal_id):
	if request.user.role != 'HOD':
		return redirect('home')

	proposal = get_object_or_404(Proposal, pk=proposal_id)
	evaluations = Evaluation.objects.filter(proposal=proposal)
	hod_user = request.user.hod

	if request.method == 'POST':
		requested_amount = Decimal(proposal.requested_amount)
          
		if requested_amount <= hod_user.total_department_budget:
			new_grant, created = Grant.objects.update_or_create(
				proposal=proposal,
				totalAllocatedAmount=request.POST.get('amount'),
				startDate=request.POST.get('start_date'),
				endDate=request.POST.get('end_date')
			)
            
			if created:
				hod_user.total_department_budget -= requested_amount
				hod_user.save()

				Budget.objects.create(
					grant=new_grant,
					remainingBalance=new_grant.totalAllocatedAmount,
					expendituresDetails="Initial allocation."
				)
                
				proposal.status = 'Approved'
				proposal.save()
                    
				messages.success(request, 'Proposal approved and grant created successfully.')
				return redirect('hod_dashboard')
		else:
			error_message = f"Insufficient department budget to approve this proposal. Your current budget is {hod_user.total_department_budget}."
			return render(request, 'grants/approve_form.html', {'proposal': proposal, 'evaluations': evaluations, 'error_message': error_message, 'hod_budget': hod_user.total_department_budget})

	return render(request, 'grants/approve_form.html', {'proposal': proposal, 'evaluations': evaluations, 'hod_budget': hod_user.total_department_budget})


@login_required
def evaluate_proposal(request, proposal_id):
    # Security: Ensure only Reviewers can access
    if request.user.role != 'Reviewer':
        return redirect('home')

    proposal = get_object_or_404(Proposal, pk=proposal_id)

    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.proposal = proposal
            evaluation.reviewer = request.user.reviewer # Link to Reviewer profile
            evaluation.save()

            # Update status so only HOD can receive it in their dashboard
            proposal.status = 'Review Complete'
            proposal.save()

            return redirect('reviewer_dashboard')
    else:
        form = EvaluationForm()

    return render(request, 'grants/evaluate_proposal.html', {
        'form': form,
        'proposal': proposal
    })