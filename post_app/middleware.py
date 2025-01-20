import uuid
from django.http import JsonResponse
from django.urls import resolve


class UUIDValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.check_uuid_in_url(request)
        if response:
            return response
        return self.get_response(request)

    def check_uuid_in_url(self, request):
        try:
            resolved = resolve(request.path_info)
            url_params = resolved.kwargs
            print(f"{url_params = }")
           
        except Exception as e:
            return None
        
        for param, value in url_params.items():
            if not self.is_valid_uuid(value):
                return JsonResponse(
                    {"detail": f"The provided {param} UUID is not in a valid format."},
                    status=400
                )
        return None

    def is_valid_uuid(self, value):
        if isinstance(value, str):
            try:
                uuid_obj = uuid.UUID(value)
                is_valid = str(uuid_obj) == value
                return is_valid
            except ValueError:
                
                return False
        return False
