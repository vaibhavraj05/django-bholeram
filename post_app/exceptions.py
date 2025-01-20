from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
def custom_exception_handler(exc, context):
    """
    Custom exception handler for global error formatting.
    """
    # Call the default exception handler first
    response = exception_handler(exc, context)
    if response is not None:
        # Customize error message formatting only for 400 errors (bad requests)
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            response.data = format_errors(response.data)
        
        # Example: Handle other errors like permission denied
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            response.data = {"detail": "You do not have permission to perform this action."}
        
    # Check if there's a validation error (or any other error you want to handle)
    if response is not None and response.status_code == status.HTTP_400_BAD_REQUEST:
        # Modify the error format
        response.data = format_errors(response.data)
    
    return response

def format_errors(errors):
    """
    Customize the error message format globally.
    This function flattens the error message list into a string with new lines.
    """
    error_messages = []

    for field, messages in errors.items():
        for message in messages:
            # Add each error message to the list with the field name
            error_messages.append(f"{field}: {message}")
    
    # Join all error messages with a newline character, so they appear on separate lines
    return {"detail": "\n".join(error_messages)}
