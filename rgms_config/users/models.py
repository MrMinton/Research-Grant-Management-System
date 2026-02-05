from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

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

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=200, blank=True, null=True, help_text="URL to redirect to")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message}"