from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Proposal, Grant, Budget, Evaluation, ProgressReport
from .forms import ProposalForm, ProgressReportForm, EvaluationForm
from decimal import Decimal
from django.db.models import Max
from django.db.models import Sum, Count
from django.db.models import Max
from users.models import Notification


@login_required
def researcher_dashboard(request):
    if request.user.role != 'Researcher':
        return redirect('home') 
    
    # 1. Fetch ALL proposals for this researcher
    all_proposals = Proposal.objects.filter(researcher=request.user.researcher)
    
    # 2. FILTER: Keep only the latest version of each proposal (Group by Title)
    latest_proposals_map = {}
    
    for p in all_proposals:
        # If we haven't seen this title yet, or if this version is higher than what we have stored
        if p.title not in latest_proposals_map:
            latest_proposals_map[p.title] = p
        else:
            if p.version > latest_proposals_map[p.title].version:
                latest_proposals_map[p.title] = p

    # Convert the dictionary back to a list and sort by Date (newest first)
    my_proposals = sorted(latest_proposals_map.values(), key=lambda x: x.submissionDate, reverse=True)
    
    return render(request, 'grants/researcher_dashboard.html', {'proposals': my_proposals})

login_required
def submit_proposal(request):
    if request.user.role != 'Researcher':
        return redirect('home')
    
    if request.method == 'POST':
        form = ProposalForm(request.POST, request.FILES)
        if form.is_valid():
            new_proposal = form.save(commit=False)
            new_proposal.researcher = request.user.researcher
            
            existing_proposals = Proposal.objects.filter(
                researcher=request.user.researcher, 
                title=new_proposal.title
            )
            
            if existing_proposals.exists():
                current_max = existing_proposals.aggregate(Max('version'))['version__max']
                new_proposal.version = current_max + 0.1 
                messages.success(request, f"New version {new_proposal.version:.1f} submitted successfully!")
            else:
                new_proposal.version = 1.0
                messages.success(request, "Proposal submitted successfully!")

            if new_proposal.pdf_file:
                new_proposal.status = 'Pending'
            else:
                new_proposal.status = 'Draft'

            new_proposal.save()
            return redirect('researcher_dashboard')
        
        else:
            # --- ADDED: Error Feedback ---
            messages.error(request, "Submission failed. Please check for file type or other errors.")
            # -----------------------------
            
    else:
        form = ProposalForm()
        
    return render(request, 'grants/submit_proposal.html', {'form': form})

@login_required
def resubmit_proposal(request, proposal_id):
    if request.user.role != 'Researcher':
        return redirect('home')
        
    # Get the original proposal to pre-fill data
    original_proposal = get_object_or_404(Proposal, pk=proposal_id)
    
    if request.method == 'POST':
        form = ProposalForm(request.POST, request.FILES)
        if form.is_valid():
            new_proposal = form.save(commit=False)
            new_proposal.researcher = request.user.researcher
            
            # FORCE match the title so versioning logic works
            new_proposal.title = original_proposal.title
            
            # CALCULATE NEW VERSION
            # Find all proposals with this title to get the absolute max version
            existing_proposals = Proposal.objects.filter(
                researcher=request.user.researcher, 
                title=original_proposal.title
            )
            current_max = existing_proposals.aggregate(Max('version'))['version__max']
            new_proposal.version = current_max + 0.1
            
            # Reset status for review
            new_proposal.status = 'Pending'
            
            new_proposal.save()
            messages.success(request, f"Version {new_proposal.version:.1f} submitted successfully! It has replaced the old version on your dashboard.")
            return redirect('researcher_dashboard')
    else:
        # Pre-fill form
        form = ProposalForm(initial={
            'title': original_proposal.title,
            'requested_amount': original_proposal.requested_amount
        })

    return render(request, 'grants/submit_proposal.html', {
        'form': form, 
        'original_proposal': original_proposal
    })

@login_required
def grant_detail(request, proposal_id):
    if request.user.role != 'Researcher':
        return redirect('home')

    proposal = get_object_or_404(Proposal, pk=proposal_id)
    
    # 1. FIX: Fetch reports explicitly sorted by Newest First (-submissionDate)
    # We also sort by -reportID to ensure even reports on the same day stay in order
    reports = proposal.progressreport_set.all().order_by('-submissionDate', '-reportID')
    
    # Logic: Calculate Budget Percentage
    usage_percent = 0
    grant = None
    budget = None

    try:
        grant = proposal.grant
        budget = grant.budget
        if grant.totalAllocatedAmount > 0:
            usage_percent = (budget.totalSpent / grant.totalAllocatedAmount) * 100
    except (Grant.DoesNotExist, Budget.DoesNotExist):
        pass 

    return render(request, 'grants/grant_detail.html', {
        'proposal': proposal,
        'grant': grant,
        'budget': budget,
        'usage_percent': round(usage_percent, 1),
        'reports': reports # 2. Pass the sorted list to the template
    })

@login_required
def submit_report(request, proposal_id):
    if request.user.role != 'Researcher':
        return redirect('home')

    proposal = get_object_or_404(Proposal, pk=proposal_id)

    if request.method == 'POST':
        form = ProgressReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.proposal = proposal
            report.save()

            # --- LOGIC: UPDATE BUDGET TOTAL SPENT ---
            try:
                # 1. Get the grant and budget associated with this proposal
                grant = proposal.grant
                budget = grant.budget
                
                # 2. Add the report's expenditure to the total spent
                if report.expenditure_amount > 0:
                    budget.totalSpent += report.expenditure_amount
                    budget.save()
                    
            except (Grant.DoesNotExist, Budget.DoesNotExist):
                # If for some reason grant/budget doesn't exist, ignore financial update
                pass

            messages.success(request, "Progress report submitted successfully.")
            return redirect('grant_detail', proposal_id=proposal.proposalID)
    else:
        form = ProgressReportForm()

    return render(request, 'grants/submit_report.html', {'form': form, 'proposal': proposal})



@login_required
def reviewer_dashboard(request):
    # 1. Security check: Ensure the user is actually a Reviewer
    if request.user.role != 'Reviewer':
        return redirect('home')

    # 2. Get proposals. 
    # Reviewers should see everything that is NOT a 'Draft'.

    proposals_to_review = Proposal.objects.all()
    
    # Get list of already evaluated proposals
    evaluated_ids = Evaluation.objects.filter(
        reviewer=request.user.reviewer
    ).values_list('proposal_id', flat=True)

    context = {
        'proposals': proposals_to_review,
        'evaluated_ids': evaluated_ids
    }
    return render(request, 'users/reviewer_dashboard.html', context)


# HOD PART

@login_required
def hod_dashboard(request):
    if request.user.role != 'HOD':
        return redirect('home')

    # Pending
    proposals = Proposal.objects.filter(status='Review Complete')
    
    # Active
    active_grants = Grant.objects.all()

    # Rejected History (NEW)
    rejected_proposals = Proposal.objects.filter(status='Rejected').order_by('-submissionDate')[:5] # Show last 5

    return render(request, 'grants/hod_dashboard.html', {
        'proposals': proposals,
        'active_grants': active_grants,
        'rejected_proposals': rejected_proposals # Pass to template
    })

@login_required
def approve_proposal(request, proposal_id):
    if request.user.role != 'HOD':
        return redirect('home')

    proposal = get_object_or_404(Proposal, pk=proposal_id)
    evaluations = Evaluation.objects.filter(proposal=proposal)
    hod_user = request.user.hod

    if request.method == 'POST':
        # 1. CHECK THE ACTION (Approve vs Reject)
        action = request.POST.get('action')

        if action == 'reject':
            # --- REJECTION LOGIC ---
            proposal.status = 'Rejected'
            proposal.save()

            # Notify Researcher
            Notification.objects.create(
                recipient=proposal.researcher,
                message=f"Update: Your proposal '{proposal.title}' has been REJECTED by the HOD.",
                link=f"/grant/{proposal.proposalID}/" 
            )
            
            messages.info(request, f"Proposal '{proposal.title}' has been rejected.")
            return redirect('hod_dashboard')

        elif action == 'approve':
            # --- EXISTING APPROVAL LOGIC ---
            try:
                allocated_amount = Decimal(request.POST.get('amount'))
            except (ValueError, TypeError):
                messages.error(request, "Invalid amount entered.")
                return redirect('approve_proposal', proposal_id=proposal.proposalID)

            # Validation: Check against Department Budget
            if allocated_amount > hod_user.total_department_budget:
                error_message = f"Insufficient funds. You tried to allocate RM{allocated_amount}, but have only RM{hod_user.total_department_budget}."
                return render(request, 'grants/approve_form.html', {
                    'proposal': proposal, 
                    'evaluations': evaluations, 
                    'error_message': error_message, 
                    'hod_budget': hod_user.total_department_budget
                })

            # Create Grant
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

                Notification.objects.create(
                    recipient=proposal.researcher,
                    message=f"Good news! Your proposal '{proposal.title}' has been APPROVED.",
                    link=f"/grant/{proposal.proposalID}/"
                )
                    
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
	# --- NEW: CALCULATE TIME ELAPSED % ---
    today = timezone.now().date()
    total_days = (grant.endDate - grant.startDate).days
    elapsed_days = (today - grant.startDate).days

    if total_days > 0:
        time_progress = round((elapsed_days / total_days) * 100)
    else:
        time_progress = 100 
    
    # Ensure it stays between 0% and 100%
    time_progress = max(0, min(100, time_progress))
    

    if request.method == 'POST':
        action_request = request.POST.get('feedback')
        status_flag = request.POST.get('status_flag') # e.g., 'On Track' or 'Needs Intervention'

        if action_request:
            # 1. LOGIC: Choose the prefix based on the status
            if status_flag == 'Needs Intervention':
                prefix = "URGENT INTERVENTION"
                milestone_text = "⚠ Status set to Needs Intervention"
                # More alarming notification message
                notif_msg = f"URGENT: HOD requires intervention on '{proposal.title}'. See feedback."
            else:
                prefix = "HOD FEEDBACK"
                milestone_text = f"✔ Status set to {status_flag}"
                # Standard notification message
                notif_msg = f"Update: HOD sent feedback for '{proposal.title}': {status_flag}"

            # 2. Create the Report with the correct label
            ProgressReport.objects.create(
                proposal=proposal,
                content=f"{prefix}: {action_request}",
                milestonesAchieved=milestone_text 
            )
            
            proposal.status = status_flag
            proposal.save()

            # --- NOTIFICATION TRIGGER ---
            Notification.objects.create(
                recipient=proposal.researcher,
                message=notif_msg,
                link=f"/grant/{proposal.proposalID}/"
            )
            
            messages.success(request, f"Feedback sent and status updated to {status_flag}.")
            return redirect('hod_dashboard')

    return render(request, 'grants/project_monitoring_detail.html', {
        'grant': grant,
        'proposal': proposal,
        'reports': reports,
        'time_progress': time_progress
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
                
                hod_user.total_department_budget -= additional_funds
                hod_user.save()

                # --- NOTIFICATION 3: BUDGET TOP-UP ---
                Notification.objects.create(
                    recipient=grant.proposal.researcher,
                    message=f"Budget Alert: Top-up of RM{additional_funds} approved for '{grant.proposal.title}'.",
                    link=f"/grant/{grant.proposal.proposalID}/"
                )
                
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


@login_required
def hod_analytics(request):
    if request.user.role != 'HOD':
        return redirect('home')

    # --- 1. BUDGET CALCULATIONS ---
    # Aggregate total spent from all budgets
    spending_data = Budget.objects.aggregate(total=Sum('totalSpent'))
    total_spent = spending_data['total'] or 0
    
    # Calculate remaining based on the HOD's limit
    remaining_funds = request.user.hod.total_department_budget

    # --- 2. KPI: ACTIVE GRANTS ---
    # We count grants that are currently running
    active_grants_count = Grant.objects.count()

    # --- 3. SUCCESS METRICS (Accept vs Reject) ---
    total_props = Proposal.objects.count()
    approved_props = Proposal.objects.filter(status='Approved').count()
    rejected_props = Proposal.objects.filter(status='Rejected').count()
    
    if total_props > 0:
        approval_rate = round((approved_props / total_props) * 100, 1)
        rejection_rate = round(rejected_props / total_props * 100, 1)
    else:
        # Avoid showing "100% Rejected" if there are 0 proposals
        approval_rate = 0
        rejection_rate = 0

    return render(request, 'grants/hod_analytics.html', {
        'total_spent': float(total_spent),
        'remaining_funds': float(remaining_funds),
        'active_grants_count': active_grants_count,
        'approval_rate': approval_rate,
        'rejection_rate': rejection_rate
    })


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

            # Update status so HOD can see it
            proposal.status = 'Review Complete'
            proposal.save()

            # --- NOTIFICATION TRIGGER ---
            Notification.objects.create(
                recipient=proposal.researcher,
                message=f"Update: A reviewer has evaluated '{proposal.title}'.",
                link=f"/grant/{proposal.proposalID}/"
            )

            messages.success(request, f"Evaluation submitted for {proposal.title}.")
            return redirect('reviewer_dashboard')
    else:
        form = EvaluationForm()

    return render(request, 'grants/evaluate_proposal.html', {
        'form': form,
        'proposal': proposal
    })



@login_required
def view_evaluation(request, proposal_id):
    if request.user.role != 'Reviewer':
        return redirect('home')

    proposal = get_object_or_404(Proposal, pk=proposal_id)
    
    # Fetch the evaluation specifically created by this reviewer for this proposal
    evaluation = get_object_or_404(Evaluation, proposal=proposal, reviewer=request.user.reviewer)

    return render(request, 'grants/view_evaluation.html', {
        'proposal': proposal, 
        'evaluation': evaluation
    })