from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    role_choices = [('Researcher', 'Researcher'), ('Reviewer', 'Reviewer'), ('HOD', 'HOD')]
    role = models.CharField(max_length=20, choices=role_choices)

class Researcher(User):
    department = models.CharField(max_length=100) 
    researchinterests = models.TextField() 

class Reviewer(User):
    specialization = models.CharField(max_length=100) 

class HOD(User):
    deptID = models.CharField(max_length=10) 