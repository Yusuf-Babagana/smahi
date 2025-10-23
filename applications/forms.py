from django import forms
from .models import Applicant

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = [
            'full_name', 'email', 'phone', 'address', 
            'state', 'position_applied', 'cv', 'receipt'
        ]
        
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your full address'
            }),
            'state': forms.Select(attrs={
                'class': 'form-select'
            }),
            'position_applied': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cv': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'receipt': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
        }
        
        labels = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'address': 'Home Address',
            'state': 'State of Residence',
            'position_applied': 'Position Applied For',
            'cv': 'CV/Resume',
            'receipt': 'Payment Receipt (Optional)',
        }
        
        help_texts = {
            'receipt': 'Optional: Only upload if you paid via bank transfer instead of online payment',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make receipt field optional since we have online payment
        self.fields['receipt'].required = False
        
        # Set default position to 'agent' and make it read-only
        self.fields['position_applied'].initial = 'agent'
        self.fields['position_applied'].widget.attrs['readonly'] = True
        self.fields['position_applied'].widget.attrs['style'] = 'background-color: #f8f9fa;'
    
    def clean_cv(self):
        cv = self.cleaned_data.get('cv')
        if cv:
            if cv.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('CV file size must be less than 5MB.')
        return cv
    
    def clean_receipt(self):
        receipt = self.cleaned_data.get('receipt')
        if receipt:
            if receipt.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('Receipt file size must be less than 5MB.')
        return receipt
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # If this is a new instance (not updating existing)
        if not instance.pk:
            # Set payment information from session if available
            from django.core.handlers.wsgi import WSGIRequest
            
            # Try to get request from form if available
            if hasattr(self, 'request'):
                request = self.request
                if hasattr(request, 'session'):
                    payment_email = request.session.get('payment_email')
                    payment_reference = request.session.get('payment_reference')
                    
                    if payment_email and payment_reference:
                        instance.payment_email = payment_email
                        instance.payment_reference = payment_reference
                        instance.payment_verified = True
                        instance.payment_amount = 2500.00
        
        if commit:
            instance.save()
        
        return instance