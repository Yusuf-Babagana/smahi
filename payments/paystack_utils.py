import requests
import uuid
from django.conf import settings

def initialize_payment(email, amount, callback_url=None):
    """Initialize Paystack payment"""
    url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    
    # Amount in kobo (₦2500 = 2500 * 100)
    amount_in_kobo = int(amount * 100)
    reference = str(uuid.uuid4())
    
    data = {
        'email': email,
        'amount': amount_in_kobo,
        'reference': reference,
        'callback_url': callback_url,
        'metadata': {
            'custom_fields': [
                {
                    'display_name': "Form Access Fee",
                    'variable_name': "form_access_fee",
                    'value': "Job Application Form"
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except Exception as e:
        return {'status': False, 'message': str(e)}

def verify_payment(reference):
    """Verify Paystack payment"""
    url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    }
    
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        return {'status': False, 'message': str(e)}