from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Proposal, Grant, Budget, Evaluation, ProgressReport
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
        try:
            allocated_amount = Decimal(request.POST.get('amount'))
        except (ValueError, TypeError):
            messages.error(request, "Invalid amount entered.")
            return redirect('approve_proposal', proposal_id=proposal.proposalID)

        # 2. VALIDATION: Check against Department Budget
        if allocated_amount > hod_user.total_department_budget:
            error_message = f"Insufficient funds. You tried to allocate RM{allocated_amount}, but have only RM{hod_user.total_department_budget}."
            return render(request, 'grants/approve_form.html', {
                'proposal': proposal, 
                'evaluations': evaluations, 
                'error_message': error_message, 
                'hod_budget': hod_user.total_department_budget
            })

        # 3. Create Grant with the ALLOCATED amount
        # Note: We use 'proposal' as the unique lookup, and update everything else
        grant, created = Grant.objects.update_or_create(
            proposal=proposal,
            defaults={
                'totalAllocatedAmount': allocated_amount,
                'startDate': request.POST.get('start_date'),
                'endDate': request.POST.get('end_date')
            }
        )
        
        if created:
            hod_user.total_department_budget -= allocated_amount
            hod_user.save()

            Budget.objects.create(
                grant=grant,
                totalSpent=0.0,
                expendituresDetails="Initial allocation."
            )
            
            proposal.status = 'Approved'
            proposal.save()
                
            messages.success(request, 'Proposal approved and grant created successfully.')
            return redirect('hod_dashboard')
        else:
            messages.info(request, 'Grant details updated successfully.')
            return redirect('hod_dashboard')

    return render(request, 'grants/approve_form.html', {
        'proposal': proposal, 
        'evaluations': evaluations, 
        'hod_budget': hod_user.total_department_budget
    })

@login_required
def project_detail(request, grant_id):
    if request.user.role != 'HOD':
        return redirect('home')

    grant = get_object_or_404(Grant, pk=grant_id)
    proposal = grant.proposal

    reports = ProgressReport.objects.filter(proposal=proposal).order_by('-submissionDate')

    if request.method == 'POST':
        action_request = request.POST.get('feedback')
        status_flag = request.POST.get('status_flag')

        if action_request:
            ProgressReport.objects.create(
                proposal=proposal,
                content=f"HOD INTERVENTION: {action_request}",
                milestonesAchieved="N/A - Intervention Log"
            )
            
            proposal.status = status_flag
            proposal.save()
            
            messages.success(request, f"Intervention sent for {proposal.title}.")
            return redirect('hod_dashboard')

    return render(request, 'grants/project_monitoring_detail.html', {
        'grant': grant,
        'proposal': proposal,
        'reports': reports
    })

@login_required
def track_budget(request, grant_id):
    if request.user.role != 'HOD':
        return redirect('home')

    grant = get_object_or_404(Grant, pk=grant_id)
    budget = get_object_or_404(Budget, grant=grant) 

    total_allocated = grant.totalAllocatedAmount
    
    if total_allocated > 0:
        usage_percent = (budget.totalSpent / total_allocated) * 100
    else:
        usage_percent = 0

    alert_triggered = False
    if usage_percent > 90:
        messages.error(request, f"CRITICAL ALERT: Project #{grant.grantID} has used {usage_percent:.1f}% of its budget!")
        alert_triggered = True

    # HANDLE TOP-UP / ADJUSTMENT
    if request.method == 'POST':
        try:
            additional_funds = Decimal(request.POST.get('top_up_amount'))
            hod_user = request.user.hod
            

            if hod_user.total_department_budget >= additional_funds:
                grant.totalAllocatedAmount += additional_funds
                grant.save()
                
                # budget.remainingBalance += additional_funds
                # budget.save()
                
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
                hod_user.total_department_budget -= additional_funds
                hod_user.save()
                
                messages.success(request, f"Successfully added ${additional_funds} to the project budget.")
                return redirect('track_budget', grant_id=grant.grantID)
            else:
                messages.error(request, "Insufficient department funds for this top-up.")
        except ValueError:
             messages.error(request, "Invalid amount entered.")

    return render(request, 'grants/budget_detail.html', {
        'grant': grant,
        'budget': budget,
        'totalspent': budget.totalSpent,
        'remainingbalance': budget.remainingBalance,
        'usage_percent': round(usage_percent, 1),
        'alert_triggered': alert_triggered,
        'hod_budget': request.user.hod.total_department_budget
    })