from django.db import models
from users.models import Researcher, Reviewer, HOD, User

class Proposal(models.Model):
	proposalID = models.AutoField(primary_key=True)
	requested_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0) 
	title = models.CharField(max_length=255)
	pdf_file = models.FileField(upload_to='proposals/pdfs/', null=True, blank=True)
	submissionDate = models.DateField(auto_now_add=True) 
	status = models.CharField(max_length=50, default='Draft') 
	version = models.FloatField(default=1.0) 
	researcher = models.ForeignKey(Researcher, on_delete=models.CASCADE) 

	def __str__(self):
		return f"{self.title} - {self.researcher.username}"
     
class Grant(models.Model):
	grantID = models.AutoField(primary_key=True) 
	totalAllocatedAmount = models.DecimalField(max_digits=12, decimal_places=2) 
	startDate = models.DateField()
	endDate = models.DateField() 
	proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE) 

	def __str__(self):
		return f"Grant: {self.proposal.title} ({self.proposal.status})"
	
	def get_usage_percent(self):
		if hasattr(self, 'budget') and self.totalAllocatedAmount > 0:
			percent = (self.budget.totalSpent / self.totalAllocatedAmount) * 100
			return min(int(percent), 100) # Cap at 100 for the bar width
		return 0

class Budget(models.Model):
	budgetID = models.AutoField(primary_key=True) 
	totalSpent = models.DecimalField(max_digits=12, decimal_places=2, default=0.0) 
	expendituresDetails = models.TextField(blank=True, default='') 
	grant = models.OneToOneField(Grant, on_delete=models.CASCADE) 

	def __str__(self):
		return f"Budget for Grant ID: {self.grant.grantID}"
	
	@property
	def remainingBalance(self):
		return self.grant.totalAllocatedAmount - self.totalSpent
	
class Evaluation(models.Model):
	score = models.IntegerField() 
	feedbackComments = models.TextField() 
	proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE) 
	reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE) 

	def __str__(self):
		return f"Evaluation by {self.reviewer.username} for {self.proposal.title}"
	
class ProgressReport(models.Model):
	reportID = models.AutoField(primary_key=True) 
	submissionDate = models.DateField(auto_now_add=True) 
	content = models.TextField() 
	milestonesAchieved = models.TextField() 
		
	proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE) 

	def validateSubmission(self): 
		return f"Report {self.proposal.title} submitted on {self.submissionDate}"