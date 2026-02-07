from .models import Notification

def user_notifications(request):
    # Only fetch notifications if user is logged in AND on the Researcher dashboard specifically
    if request.user.is_authenticated and request.resolver_match and request.resolver_match.url_name == 'researcher_dashboard':
        
        # Get unread notifications for the bell badge
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        
        # Get the latest 5 notifications
        latest_notifs = Notification.objects.filter(recipient=request.user)[:5]
        
        return {
            'notif_count': unread_count,
            'notifications': latest_notifs
        }
        
    # If not on a dashboard, return empty data to save performance
    return {
        'notif_count': 0,
        'notifications': []
    }