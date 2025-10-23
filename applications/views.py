from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .forms import ApplicationForm
from .models import Applicant
from payments.models import FormAccess  # Import the payment model

def landing_page(request):
    """Landing page with company information and apply button"""
    context = {
        'total_applicants': Applicant.objects.count(),
    }
    
    return render(request, 'applications/landing.html', context)

def apply_now(request):
    """Application form view - Protected by payment"""
    # Check if user has paid
    if not has_payment_access(request):
        messages.info(
            request, 
            'Please complete the ₦2,500 payment to access the application form.'
        )
        return redirect('payment_gateway')
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            applicant = form.save(commit=False)
            
            # Add payment information to applicant
            applicant.payment_email = request.session.get('payment_email')
            applicant.payment_reference = request.session.get('payment_reference')
            applicant.save()
            
            # Send confirmation email
            try:
                send_confirmation_email(applicant)
                messages.success(
                    request, 
                    'Your application has been submitted successfully! '
                    'A confirmation email has been sent to your email address.'
                )
            except Exception as e:
                messages.success(
                    request,
                    'Your application has been submitted successfully! '
                    'However, we couldn\'t send the confirmation email.'
                )
            
            # Clear payment session after successful application
            request.session.pop('payment_verified', None)
            
            return redirect('application_success', applicant_id=applicant.id)
    else:
        # Pre-fill email from payment if available
        initial_data = {}
        payment_email = request.session.get('payment_email')
        if payment_email:
            initial_data['email'] = payment_email
            
        form = ApplicationForm(initial=initial_data)
    
    return render(request, 'applications/apply.html', {'form': form})

def application_success(request, applicant_id):
    """Success page after application submission"""
    try:
        applicant = Applicant.objects.get(id=applicant_id)
    except Applicant.DoesNotExist:
        return redirect('landing_page')
    
    return render(request, 'applications/success.html', {'applicant': applicant})

def send_confirmation_email(applicant):
    """Send confirmation email to applicant"""
    subject = 'Agent Position Application Confirmation - S MAHI Global Services'
    
    # Email content
    html_message = render_to_string('applications/email_confirmation.html', {
        'applicant': applicant,
    })
    
    plain_message = f"""
    Dear {applicant.full_name},

    Thank you for your interest in joining S MAHI Global Services!

    We have successfully received your application for the Agent position.

    Application Details:
    - Name: {applicant.full_name}
    - Position: Agent
    - Email: {applicant.email}
    - Phone: {applicant.phone}
    - State: {applicant.get_state_display()}
    - Payment Reference: {applicant.payment_reference}
    - Submitted: {applicant.created_at.strftime('%B %d, %Y at %I:%M %p')}

    Our HR team will review your application and contact you within 5-7 business days.

    Best regards,
    S MAHI Global Services HR Team
    """
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[applicant.email],
        html_message=html_message,
        fail_silently=False,
    )

def has_payment_access(request):
    """Check if user has valid payment access"""
    # Check session first
    if request.session.get('payment_verified'):
        return True
    
    # Check database
    email = request.session.get('payment_email')
    if email:
        try:
            access = FormAccess.objects.get(email=email, is_active=True)
            if access.access_expires > timezone.now():
                request.session['payment_verified'] = True
                return True
        except FormAccess.DoesNotExist:
            pass
    
    return False