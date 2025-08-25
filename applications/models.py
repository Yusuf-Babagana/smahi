import os
from django.db import models
from django.core.validators import FileExtensionValidator

def cv_upload_path(instance, filename):
    return f'cv/{filename}'

def receipt_upload_path(instance, filename):
    return f'receipts/{filename}'

class Applicant(models.Model):
    POSITION_CHOICES = [
        ('agent', 'Agent'),
    ]
    
    STATE_CHOICES = [
        ('abia', 'Abia'),
        ('adamawa', 'Adamawa'),
        ('akwa_ibom', 'Akwa Ibom'),
        ('anambra', 'Anambra'),
        ('bauchi', 'Bauchi'),
        ('bayelsa', 'Bayelsa'),
        ('benue', 'Benue'),
        ('borno', 'Borno'),
        ('cross_river', 'Cross River'),
        ('delta', 'Delta'),
        ('ebonyi', 'Ebonyi'),
        ('edo', 'Edo'),
        ('ekiti', 'Ekiti'),
        ('enugu', 'Enugu'),
        ('fct', 'Federal Capital Territory'),
        ('gombe', 'Gombe'),
        ('imo', 'Imo'),
        ('jigawa', 'Jigawa'),
        ('kaduna', 'Kaduna'),
        ('kano', 'Kano'),
        ('katsina', 'Katsina'),
        ('kebbi', 'Kebbi'),
        ('kogi', 'Kogi'),
        ('kwara', 'Kwara'),
        ('lagos', 'Lagos'),
        ('nasarawa', 'Nasarawa'),
        ('niger', 'Niger'),
        ('ogun', 'Ogun'),
        ('ondo', 'Ondo'),
        ('osun', 'Osun'),
        ('oyo', 'Oyo'),
        ('plateau', 'Plateau'),
        ('rivers', 'Rivers'),
        ('sokoto', 'Sokoto'),
        ('taraba', 'Taraba'),
        ('yobe', 'Yobe'),
        ('zamfara', 'Zamfara'),
    ]
    
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    state = models.CharField(max_length=50, choices=STATE_CHOICES)
    position_applied = models.CharField(max_length=50, choices=POSITION_CHOICES)
    
    cv = models.FileField(
        upload_to=cv_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        help_text="Upload your CV/Resume (PDF, DOC, DOCX only)"
    )
    
    receipt = models.FileField(
        upload_to=receipt_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text="Upload payment receipt (PDF, JPG, PNG only)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Job Applicant'
        verbose_name_plural = 'Job Applicants'
    
    def __str__(self):
        return f"{self.full_name} - {self.get_position_applied_display()}"
    
    @property
    def cv_filename(self):
        return os.path.basename(self.cv.name) if self.cv else "No CV uploaded"
    
    @property
    def receipt_filename(self):
        return os.path.basename(self.receipt.name) if self.receipt else "No receipt uploaded"