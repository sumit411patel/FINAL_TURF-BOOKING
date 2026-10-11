from django.shortcuts import redirect
from turf.models import login

class AdminAccessRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        
        # Paths that the admin should be able to access
        allowed_prefixes = [
            '/myadmin/',
            '/admin/',
            '/media/',
            '/static/',
        ]
        
        allowed_exact_paths = [
            '/logout',
            '/logout/',
        ]
        
        is_restricted_for_admin = True
        
        if path in allowed_exact_paths:
            is_restricted_for_admin = False
        else:
            for prefix in allowed_prefixes:
                if path.startswith(prefix):
                    is_restricted_for_admin = False
                    break
        
        if is_restricted_for_admin:
            uid = request.session.get('login_id')
            if uid:
                try:
                    user = login.objects.get(id=uid)
                    if user.user_type == 'admin':
                        return redirect('/myadmin/dashboard')
                except login.DoesNotExist:
                    pass
                
        response = self.get_response(request)
        return response
