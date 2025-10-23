from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from .models import FormAccess

class PaymentRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define paths that require payment
        self.protected_paths = [
            '/apply/',           # Application form
            '/application/',     # Alternative application paths
        ]
        
        # Define paths that are exempt from payment check
        self.exempt_paths = [
            '/payment/',         # Payment pages
            '/admin/',           # Admin site
            '/media/',           # Media files
            '/static/',          # Static files
            '/success/',         # Success pages
            '/landing/',         # Landing page
            '/',                 # Home page (if it's landing)
        ]

    def __call__(self, request):
        # Check if current path requires payment
        path_requires_payment = any(
            request.path.startswith(protected_path) 
            for protected_path in self.protected_paths
        )
        
        # Check if current path is exempt
        path_is_exempt = any(
            request.path.startswith(exempt_path) 
            for exempt_path in self.exempt_paths
        )
        
        if path_requires_payment and not path_is_exempt:
            # Check if user has payment access
            if not self.has_payment_access(request):
                # Redirect to payment gateway
                return redirect('payment_gateway')
        
        return self.get_response(request)
    
    def has_payment_access(self, request):
        """Check if user has valid payment access"""
        # Check session first (immediate access after payment)
        if request.session.get('payment_verified'):
            return True
        
        # Check database for active access
        email = request.session.get('payment_email')
        if email:
            try:
                access = FormAccess.objects.get(email=email, is_active=True)
                if access.access_expires > timezone.now():
                    # Update session for future requests
                    request.session['payment_verified'] = True
                    return True
            except FormAccess.DoesNotExist:
                pass
        
        return False