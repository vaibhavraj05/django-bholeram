from .models import User

class IsUserVerified:
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if user is None or user.is_anonymous:
            email = request.data.get("email") or request.query_params.get("email")
            if email:
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    return False
            else:
                return False  
        return user.is_verified
    
    def has_object_permission(self, request, view, obj):
        # This method checks if the user has permission on a specific object
        user = request.user
        # Assuming you want to ensure the user is verified for every comment or object they interact with
        return user.is_verified
    
    



