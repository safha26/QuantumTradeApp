from django.http import HttpResponseForbidden
from functools import wraps

def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                try:
                    user_role = request.user.userprofile.role
                except Exception:
                    return HttpResponseForbidden("Access denied: No role assigned.")
                if user_role == required_role:
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponseForbidden("Access denied: Insufficient permissions.")
            else:
                return HttpResponseForbidden("Access denied: Please login.")
        return _wrapped_view
    return decorator
