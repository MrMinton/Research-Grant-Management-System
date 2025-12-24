from django.contrib import admin
from .models import Proposal, Grant, Budget, Evaluation, ProgressReport

admin.site.register([Proposal, Grant, Budget, Evaluation, ProgressReport])