"""
URL configuration for rgms_config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views # Django's built-in auth views
from users import views as user_views # Your User views
from grants import views as grant_views # Your Grant views
from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', user_views.home, name='home'),

    # --- AUTHENTICATION (Login/Logout) ---
    # We use Django's built-in LoginView but tell it to use OUR template
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    
    # We use Django's built-in LogoutView
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Dispatcher (The URL used by LOGIN_REDIRECT_URL)
    path('dashboard/', user_views.dashboard_dispatch, name='dashboard_dispatch'),

    # REVIEWER DASHBOARD URL
    path('reviewer/dashboard/', grant_views.reviewer_dashboard, name='reviewer_dashboard'),

    path('reviewer/evaluate/<int:proposal_id>/', grant_views.evaluate_proposal, name='evaluate_proposal'),
    path('reviewer/view/<int:proposal_id>/', grant_views.view_evaluation, name='view_evaluation'),
    
    # --- RESEARCHER FEATURES ---
    # Register a new account
    path('register/', user_views.register_researcher, name='register'),
    
    # The Researcher Dashboard
    # Changed path AND name to be 100% unique
    path('researcher/dashboard/', grant_views.researcher_dashboard, name='researcher_dashboard'),
    
    # Submit a new proposal
    path('submit-proposal/', grant_views.submit_proposal, name='submit_proposal'),
    # NEW: Resubmit Route
    path('resubmit/<int:proposal_id>/', grant_views.resubmit_proposal, name='resubmit_proposal'),

    path('grant/<int:proposal_id>/', grant_views.grant_detail, name='grant_detail'),    
    path('grant/report/<int:proposal_id>/', grant_views.submit_report, name='submit_report'),

	# --- HOD FEATURES ---
	path('hod/dashboard/', grant_views.hod_dashboard, name='hod_dashboard'),
    path('hod/approve/<int:proposal_id>/', grant_views.approve_proposal, name='approve_proposal'),
    path('hod/monitor/<int:grant_id>/', grant_views.project_detail, name='project_detail'),
    path('hod/budget/<int:grant_id>/', grant_views.track_budget, name='track_budget'),
    path('hod/analytics/', grant_views.hod_analytics, name='hod_analytics'),
    path('hod/analytics/export-pdf/', grant_views.export_hod_analytics_pdf, name='export_hod_analytics_pdf'),


    # --- NOTIFICATIONS ---
    path('notifications/read/', user_views.mark_notifications_read, name='mark_notifications_read'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)