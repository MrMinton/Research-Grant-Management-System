from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Reviewer, Researcher, HOD

# Register the custom User model
admin.site.register(User, UserAdmin)

# Register the Reviewer model so you can create them
admin.site.register(Reviewer)

# (Optional) Register others just in case you need to debug
admin.site.register(Researcher)
admin.site.register(HOD)
# Register your models here.
