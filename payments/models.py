from django.db import models

class PaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=2500.00)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    access_granted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.reference} - {self.email} - {self.status}"

class FormAccess(models.Model):
    email = models.EmailField(unique=True)
    payment_reference = models.CharField(max_length=100)
    access_expires = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)