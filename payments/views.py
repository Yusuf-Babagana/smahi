from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
import requests
import uuid
import json
import hmac
import hashlib
from .models import PaymentTransaction, FormAccess

def payment_gateway(request):
    """Payment gateway page"""
    if request.method == 'POST':
        email = request.POST.get('email')
        amount = 2500.00  # Fixed amount
        
        if not email:
            messages.error(request, 'Please provide a valid email address.')
            return render(request, 'payments/payment_gateway.html')
        
        # Generate unique reference
        reference = str(uuid.uuid4())
        
        # Generate callback URL
        callback_url = request.build_absolute_uri('/payment/verify/')
        
        # Initialize payment
        payment_response = initialize_payment(email, amount, reference, callback_url)
        
        if payment_response.get('status'):
            # Save transaction to database
            transaction = PaymentTransaction.objects.create(
                email=email,
                amount=amount,
                reference=reference,
                status='pending'
            )
            
            # Store email and reference in session for verification
            request.session['payment_email'] = email
            request.session['payment_reference'] = reference
            request.session['payment_in_progress'] = True
            
            # Redirect to Paystack
            return redirect(payment_response['data']['authorization_url'])
        else:
            error_message = payment_response.get('message', 'Payment initialization failed. Please try again.')
            messages.error(request, error_message)
            return render(request, 'payments/payment_gateway.html')
    
    return render(request, 'payments/payment_gateway.html')

def verify_payment_view(request):
    """Verify payment after Paystack redirect"""
    reference = request.GET.get('reference')
    email = request.session.get('payment_email')
    
    if not reference or not email:
        messages.error(request, 'Invalid payment verification. Please try the payment again.')
        return redirect('payment_gateway')
    
    # Verify payment with Paystack
    verification = verify_payment(reference)
    
    if verification.get('status') and verification['data']['status'] == 'success':
        # Update transaction status
        try:
            transaction = PaymentTransaction.objects.get(reference=reference, email=email)
            transaction.status = 'success'
            transaction.access_granted = True
            transaction.save()
            
            # Create form access (valid for 30 days)
            access_expires = timezone.now() + timedelta(days=30)
            FormAccess.objects.update_or_create(
                email=transaction.email,
                defaults={
                    'payment_reference': reference,
                    'access_expires': access_expires,
                    'is_active': True
                }
            )
            
            # Set session for immediate access
            request.session['payment_verified'] = True
            request.session['payment_email'] = transaction.email
            request.session['payment_reference'] = reference
            request.session['payment_in_progress'] = False
            
            messages.success(request, 'Payment successful! You can now access the application form.')
            return render(request, 'payments/payment_success.html', {
                'transaction': transaction
            })
            
        except PaymentTransaction.DoesNotExist:
            messages.error(request, 'Transaction not found. Please contact support.')
    else:
        # Payment failed or pending
        try:
            transaction = PaymentTransaction.objects.get(reference=reference, email=email)
            transaction.status = 'failed'
            transaction.save()
        except PaymentTransaction.DoesNotExist:
            pass
        
        error_message = verification.get('message', 'Payment verification failed. Please try again.')
        messages.error(request, error_message)
    
    # Clear payment session on failure
    request.session.pop('payment_in_progress', None)
    return render(request, 'payments/payment_failed.html')

@csrf_exempt
def payment_webhook(request):
    """Paystack webhook for server-side verification"""
    if request.method == 'POST':
        # Verify webhook signature
        payload = request.body
        signature = request.headers.get('X-Paystack-Signature', '')
        
        if not verify_webhook_signature(payload, signature):
            return JsonResponse({'status': 'invalid signature'}, status=400)
        
        try:
            data = json.loads(payload)
            
            if data.get('event') == 'charge.success':
                reference = data['data']['reference']
                email = data['data']['customer']['email']
                
                # Update or create transaction
                transaction, created = PaymentTransaction.objects.get_or_create(
                    reference=reference,
                    defaults={
                        'email': email,
                        'amount': float(data['data']['amount']) / 100,  # Convert from kobo
                        'status': 'success',
                        'access_granted': True
                    }
                )
                
                if not created and transaction.status != 'success':
                    transaction.status = 'success'
                    transaction.access_granted = True
                    transaction.save()
                
                # Create or update form access
                access_expires = timezone.now() + timedelta(days=30)
                FormAccess.objects.update_or_create(
                    email=email,
                    defaults={
                        'payment_reference': reference,
                        'access_expires': access_expires,
                        'is_active': True
                    }
                )
                
                print(f"Webhook: Payment verified for {email} - {reference}")
        
        except json.JSONDecodeError:
            return JsonResponse({'status': 'invalid JSON'}, status=400)
        except Exception as e:
            print(f"Webhook error: {str(e)}")
            return JsonResponse({'status': 'error'}, status=500)
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'method not allowed'}, status=405)

def initialize_payment(email, amount, reference, callback_url=None):
    """Initialize Paystack payment"""
    url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    
    # Convert amount to kobo (Paystack uses kobo as currency unit)
    amount_in_kobo = int(amount * 100)
    
    data = {
        'email': email,
        'amount': amount_in_kobo,
        'reference': reference,
        'callback_url': callback_url,
        'metadata': {
            'custom_fields': [
                {
                    'display_name': "Application Fee",
                    'variable_name': "application_fee",
                    'value': "Job Application Form Access"
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'status': False, 'message': f'Network error: {str(e)}'}

def verify_payment(reference):
    """Verify Paystack payment"""
    url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'status': False, 'message': f'Verification error: {str(e)}'}

def verify_webhook_signature(payload, signature):
    """Verify Paystack webhook signature"""
    computed_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        payload,
        hashlib.sha512
    ).hexdigest()
    
    return hmac.compare_digest(computed_signature, signature)

def check_payment_access(request):
    """Check if user has payment access"""
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