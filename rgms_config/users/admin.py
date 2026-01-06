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
    
admin.site.register(User, CustomUserAdmin)

# Register the profile models
admin.site.register(HOD, HODAdmin) 
admin.site.register(Reviewer, UserAdmin)
admin.site.register(Researcher, UserAdmin)