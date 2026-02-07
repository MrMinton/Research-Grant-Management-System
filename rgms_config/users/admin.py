from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Reviewer, Researcher, HOD

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Role Info', {'fields': ('role',)}),
    )
    list_display = ['username', 'email', 'role', 'is_staff']

#add budget field to HOD admin
class HODAdmin(CustomUserAdmin):
    """Specific Admin for HOD that shows User fields + DeptID."""
    fieldsets = CustomUserAdmin.fieldsets + (
        ('Department Info', {'fields': ('deptID',)}),
        ('Budget Info', {'fields': ('total_department_budget',)}),
    )

# --- Admin for Researcher ---
class ResearcherAdmin(CustomUserAdmin):
    """Specific Admin for Researcher that shows User fields + Dept + Interests."""
    fieldsets = CustomUserAdmin.fieldsets + (
        ('Researcher Details', {'fields': ('department', 'researchinterests')}),
    )
    list_display = ['username', 'email', 'department', 'role'] 

# --- Admin for Reviwer ---

class ReviewerAdmin(CustomUserAdmin):
    """Specific Admin for Reviewer."""
    fieldsets = CustomUserAdmin.fieldsets + (
        ('Department Info', {'fields': ('deptID',)}),
        ('Assigned Proposals', {'fields': ('researchinterests',)}), 
    )

admin.site.register(User, CustomUserAdmin)

# Register the profile models
admin.site.register(HOD, HODAdmin) 
admin.site.register(Reviewer, ReviewerAdmin)
admin.site.register(Researcher, ResearcherAdmin)