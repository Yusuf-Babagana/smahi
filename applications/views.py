from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.http import JsonResponse
from .forms import ApplicationForm
from .models import Applicant

def landing_page(request):
    """Landing page with company information and apply button"""
    context = {
        'total_applicants': Applicant.objects.count(),
    }
    
    return render(request, 'applications/landing.html', context)

def apply_now(request):
    """Application form view"""
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            applicant = form.save()
            
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
            
            return redirect('application_success', applicant_id=applicant.id)
    else:
        form = ApplicationForm()
    
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