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
            'receipt': 'Payment Receipt (₦2,500)',
        }
        
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