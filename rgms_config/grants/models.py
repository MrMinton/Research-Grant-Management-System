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

class Grant(models.Model):
    grantID = models.AutoField(primary_key=True) 
    totalAllocatedAmount = models.DecimalField(max_digits=12, decimal_places=2) 
    startDate = models.DateField()
    endDate = models.DateField() 
    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE) 

class Budget(models.Model):
    budgetID = models.AutoField(primary_key=True) 
    totalSpent = models.DecimalField(max_digits=12, decimal_places=2, default=0.0) 
    remainingBalance = models.DecimalField(max_digits=12, decimal_places=2)
    expendituresDetails = models.TextField(blank=True, default='') 
    grant = models.OneToOneField(Grant, on_delete=models.CASCADE) 

class Evaluation(models.Model):
    score = models.IntegerField() 
    feedbackComments = models.TextField() 
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE) 
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE) 

class ProgressReport(models.Model):
    reportID = models.AutoField(primary_key=True) 
    submissionDate = models.DateField(auto_now_add=True) 
    content = models.TextField() 
    milestonesAchieved = models.TextField() 
    
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE) 

    def validateSubmission(self): 
        """Logic for Section 5.1.6: HOD Monitoring"""
        pass