from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    role_choices = [('Researcher', 'Researcher'), ('Reviewer', 'Reviewer'), ('HOD', 'HOD')]
    role = models.CharField(max_length=20, choices=role_choices)

class Researcher(User):
    department = models.CharField(max_length=100) 
    researchinterests = models.TextField() 

    class Meta:
        verbose_name = "Researcher"
        verbose_name_plural = "Researchers"

class Reviewer(User):
    specialization = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Reviewer"
        verbose_name_plural = "Reviewers" 

class HOD(User):
    deptID = models.CharField(max_length=10)
    
    total_department_budget = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=500000.00, 
        help_text="Total funds available for the department"
    )

    class Meta:
        verbose_name = "HOD"
        verbose_name_plural = "HODs"